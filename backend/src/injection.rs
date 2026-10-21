use std::collections::BTreeMap;
use std::fmt;
use std::path::{Path, PathBuf};
use std::process::{Child, Command};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct InjectionRequest {
    pub program: PathBuf,
    pub args: Vec<String>,
    pub hook_dir: PathBuf,
    pub audit_file: Option<PathBuf>,
    pub launch_id: String,
    pub overrides: BTreeMap<String, String>,
    pub base_environment: BTreeMap<String, String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct InjectionEnvironment {
    pub variables: BTreeMap<String, String>,
}

impl InjectionEnvironment {
    pub fn get(&self, name: &str) -> Option<&str> {
        self.variables.get(name).map(String::as_str)
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum InjectionError {
    HookMissing(PathBuf),
    AuditUnavailable(PathBuf),
    InstallDirectoryForbidden(PathBuf),
    ReservedOverride(String),
    EmptyLaunchId,
}

impl fmt::Display for InjectionError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::HookMissing(path) => {
                write!(f, "hook directory is unavailable: {}", path.display())
            }
            Self::AuditUnavailable(path) => {
                write!(f, "audit destination is unavailable: {}", path.display())
            }
            Self::InstallDirectoryForbidden(path) => write!(
                f,
                "injection output is inside TOPAZ_INSTALL_DIR and is forbidden: {}",
                path.display()
            ),
            Self::ReservedOverride(name) => {
                write!(f, "override cannot replace hook control variable: {name}")
            }
            Self::EmptyLaunchId => f.write_str("launch_id must not be empty"),
        }
    }
}

fn path_is_within(child: &Path, parent: &Path) -> bool {
    child.starts_with(parent)
}

fn is_reserved_override(name: &str) -> bool {
    name == "PYTHONPATH" || name.starts_with("TOPAZ_SLP_")
}

fn path_separator() -> &'static str {
    if cfg!(windows) { ";" } else { ":" }
}

pub fn assemble_environment(
    request: &InjectionRequest,
) -> Result<InjectionEnvironment, InjectionError> {
    if request.launch_id.trim().is_empty() {
        return Err(InjectionError::EmptyLaunchId);
    }
    if !request.hook_dir.is_dir() {
        return Err(InjectionError::HookMissing(request.hook_dir.clone()));
    }

    let install_dir = request
        .base_environment
        .get("TOPAZ_INSTALL_DIR")
        .map(PathBuf::from);
    if let Some(install_dir) = install_dir.as_deref()
        && path_is_within(&request.hook_dir, install_dir)
    {
        return Err(InjectionError::InstallDirectoryForbidden(
            request.hook_dir.clone(),
        ));
    }

    let audit_file = request
        .audit_file
        .as_ref()
        .ok_or_else(|| InjectionError::AuditUnavailable(PathBuf::from("<unset>")))?;
    if let Some(install_dir) = install_dir.as_deref()
        && path_is_within(audit_file, install_dir)
    {
        return Err(InjectionError::InstallDirectoryForbidden(
            audit_file.clone(),
        ));
    }
    let audit_parent = audit_file.parent().unwrap_or_else(|| Path::new("."));
    if !audit_parent.is_dir() {
        return Err(InjectionError::AuditUnavailable(audit_file.clone()));
    }

    for name in request.overrides.keys() {
        if is_reserved_override(name) {
            return Err(InjectionError::ReservedOverride(name.clone()));
        }
    }

    let mut variables = request.base_environment.clone();
    let hook_path = request.hook_dir.to_string_lossy().into_owned();
    let python_path = variables
        .get("PYTHONPATH")
        .filter(|value| !value.is_empty())
        .map(|value| format!("{}{}{}", hook_path, path_separator(), value))
        .unwrap_or(hook_path);
    variables.insert("PYTHONPATH".to_owned(), python_path);
    variables.insert("TOPAZ_SLP_OVERRIDE_ENABLE".to_owned(), "1".to_owned());
    variables.insert(
        "TOPAZ_SLP_OVERRIDE_AUDIT_FILE".to_owned(),
        audit_file.to_string_lossy().into_owned(),
    );
    variables.insert("TOPAZ_SLP_LAUNCH_ID".to_owned(), request.launch_id.clone());
    for (name, value) in &request.overrides {
        variables.insert(name.clone(), value.clone());
    }

    Ok(InjectionEnvironment { variables })
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct FallbackEvent {
    pub code: String,
    pub reason: String,
    pub injected: bool,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum LaunchMode {
    Injected,
    NativeFallback,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LaunchPlan {
    pub program: PathBuf,
    pub args: Vec<String>,
    pub mode: LaunchMode,
    pub environment: BTreeMap<String, String>,
    pub fallback: Option<FallbackEvent>,
}

pub fn plan_launch(request: &InjectionRequest) -> LaunchPlan {
    match assemble_environment(request) {
        Ok(environment) => LaunchPlan {
            program: request.program.clone(),
            args: request.args.clone(),
            mode: LaunchMode::Injected,
            environment: environment.variables,
            fallback: None,
        },
        Err(error) => LaunchPlan {
            program: request.program.clone(),
            args: request.args.clone(),
            mode: LaunchMode::NativeFallback,
            environment: request.base_environment.clone(),
            fallback: Some(FallbackEvent {
                code: match error {
                    InjectionError::HookMissing(_) => "hook_missing",
                    InjectionError::AuditUnavailable(_) => "audit_unavailable",
                    InjectionError::InstallDirectoryForbidden(_) => "install_directory_forbidden",
                    InjectionError::ReservedOverride(_) => "reserved_override",
                    InjectionError::EmptyLaunchId => "invalid_launch_id",
                }
                .to_owned(),
                reason: error.to_string(),
                injected: false,
            }),
        },
    }
}

impl LaunchPlan {
    pub fn spawn(&self) -> std::io::Result<Child> {
        let mut command = Command::new(&self.program);
        command.args(&self.args).env_clear().envs(&self.environment);
        command.spawn()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn temp_dir(name: &str) -> PathBuf {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("clock")
            .as_nanos();
        let path = std::env::temp_dir().join(format!("starlight-{name}-{stamp}"));
        fs::create_dir_all(&path).expect("temp directory");
        path
    }

    fn request(root: &Path) -> InjectionRequest {
        let hook = root.join("hook");
        fs::create_dir_all(&hook).expect("hook");
        InjectionRequest {
            program: PathBuf::from("Topaz Video.exe"),
            args: vec!["--render".to_owned()],
            hook_dir: hook,
            audit_file: Some(root.join("audit.jsonl")),
            launch_id: "launch-1".to_owned(),
            overrides: BTreeMap::new(),
            base_environment: BTreeMap::from([("PYTHONPATH".to_owned(), "existing".to_owned())]),
        }
    }

    #[test]
    fn assembles_pythonpath_and_never_writes_files() {
        let root = temp_dir("environment");
        let request = request(&root);
        let before = fs::read_dir(&root).expect("read root").count();
        let environment = assemble_environment(&request).expect("environment");
        let expected = format!("{}{}existing", request.hook_dir.display(), path_separator());
        assert_eq!(environment.get("PYTHONPATH"), Some(expected.as_str()));
        assert_eq!(environment.get("TOPAZ_SLP_OVERRIDE_ENABLE"), Some("1"));
        assert_eq!(environment.get("TOPAZ_SLP_LAUNCH_ID"), Some("launch-1"));
        assert_eq!(fs::read_dir(&root).expect("read root").count(), before);
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn pythonpath_override_is_reserved() {
        let root = temp_dir("reserved-pythonpath");
        let mut request = request(&root);
        request
            .overrides
            .insert("PYTHONPATH".to_owned(), "elsewhere".to_owned());
        let error = assemble_environment(&request).expect_err("reserved override");
        assert_eq!(
            error,
            InjectionError::ReservedOverride("PYTHONPATH".to_owned())
        );
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn non_reserved_override_merges_into_environment() {
        let root = temp_dir("override-merge");
        let mut request = request(&root);
        request
            .overrides
            .insert("STARLIGHT_TEST_FLAG".to_owned(), "on".to_owned());
        let environment = assemble_environment(&request).expect("environment");
        assert_eq!(environment.get("STARLIGHT_TEST_FLAG"), Some("on"));

        request
            .overrides
            .insert("TOPAZ_SLP_PIX_CHUNK_SIZE".to_owned(), "121".to_owned());
        assert_eq!(
            assemble_environment(&request).expect_err("reserved override"),
            InjectionError::ReservedOverride("TOPAZ_SLP_PIX_CHUNK_SIZE".to_owned())
        );
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn audit_file_none_uses_native_fallback_with_reason() {
        let root = temp_dir("audit-none");
        let mut request = request(&root);
        request.audit_file = None;
        let plan = plan_launch(&request);
        assert_eq!(plan.mode, LaunchMode::NativeFallback);
        assert_eq!(
            plan.fallback.as_ref().map(|event| event.code.as_str()),
            Some("audit_unavailable")
        );
        assert!(
            plan.fallback
                .as_ref()
                .expect("fallback")
                .reason
                .contains("audit destination is unavailable")
        );
        assert_eq!(plan.environment, request.base_environment);
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn audit_parent_missing_uses_native_fallback_with_reason() {
        let root = temp_dir("audit-parent-missing");
        let mut request = request(&root);
        request.audit_file = Some(root.join("missing").join("audit.jsonl"));
        let plan = plan_launch(&request);
        assert_eq!(plan.mode, LaunchMode::NativeFallback);
        assert_eq!(
            plan.fallback.as_ref().map(|event| event.code.as_str()),
            Some("audit_unavailable")
        );
        assert!(
            plan.fallback
                .as_ref()
                .expect("fallback")
                .reason
                .contains("audit destination is unavailable")
        );
        assert_eq!(plan.environment, request.base_environment);
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn audit_file_inside_install_directory_uses_native_fallback_with_reason() {
        let root = temp_dir("audit-install-boundary");
        let install = root.join("Topaz");
        fs::create_dir_all(&install).expect("install");
        let mut request = request(&root);
        request.base_environment.insert(
            "TOPAZ_INSTALL_DIR".to_owned(),
            install.to_string_lossy().into_owned(),
        );
        request.audit_file = Some(install.join("audit.jsonl"));
        let plan = plan_launch(&request);
        assert_eq!(plan.mode, LaunchMode::NativeFallback);
        assert_eq!(
            plan.fallback.as_ref().map(|event| event.code.as_str()),
            Some("install_directory_forbidden")
        );
        assert_eq!(plan.environment, request.base_environment);
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn reserved_prefix_rejects_future_control_variables() {
        let root = temp_dir("reserved-prefix-future");
        let mut request = request(&root);
        request
            .base_environment
            .insert("TOPAZ_SLP_LAUNCH_ID".to_owned(), request.launch_id.clone());
        for name in ["TOPAZ_SLP_LAUNCH_ID", "TOPAZ_SLP_ANY_FUTURE_FLAG"] {
            request.overrides.clear();
            request
                .overrides
                .insert(name.to_owned(), "spoofed".to_owned());
            assert_eq!(
                assemble_environment(&request).expect_err("reserved prefix"),
                InjectionError::ReservedOverride(name.to_owned())
            );
            let plan = plan_launch(&request);
            assert_eq!(plan.mode, LaunchMode::NativeFallback);
            assert_eq!(
                plan.fallback.as_ref().map(|event| event.code.as_str()),
                Some("reserved_override")
            );
            assert_eq!(
                plan.environment.get("TOPAZ_SLP_LAUNCH_ID"),
                Some(&request.launch_id)
            );
        }
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn assembles_pythonpath_without_existing_value() {
        let root = temp_dir("pythonpath-empty");
        let mut request = request(&root);
        request.base_environment.remove("PYTHONPATH");
        let environment = assemble_environment(&request).expect("environment");
        assert_eq!(
            environment.get("PYTHONPATH"),
            Some(request.hook_dir.to_string_lossy().as_ref())
        );
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn missing_hook_uses_native_fallback_with_reason() {
        let root = temp_dir("fallback");
        let mut request = request(&root);
        request.hook_dir = root.join("missing");
        let plan = plan_launch(&request);
        assert_eq!(plan.mode, LaunchMode::NativeFallback);
        assert_eq!(
            plan.fallback.as_ref().map(|event| event.code.as_str()),
            Some("hook_missing")
        );
        assert_eq!(plan.environment, request.base_environment);
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn install_directory_is_a_hard_boundary() {
        let root = temp_dir("install-boundary");
        let install = root.join("Topaz");
        fs::create_dir_all(&install).expect("install");
        let mut request = request(&root);
        request.base_environment.insert(
            "TOPAZ_INSTALL_DIR".to_owned(),
            install.to_string_lossy().into_owned(),
        );
        request.hook_dir = install.join("hook");
        fs::create_dir_all(&request.hook_dir).expect("hook");
        let plan = plan_launch(&request);
        assert_eq!(plan.mode, LaunchMode::NativeFallback);
        assert_eq!(
            plan.fallback.as_ref().map(|event| event.code.as_str()),
            Some("install_directory_forbidden")
        );
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn reserved_override_cannot_disable_injection() {
        let root = temp_dir("reserved-override");
        let mut request = request(&root);
        request
            .overrides
            .insert("TOPAZ_SLP_OVERRIDE_ENABLE".to_owned(), "0".to_owned());
        let plan = plan_launch(&request);
        assert_eq!(plan.mode, LaunchMode::NativeFallback);
        assert_eq!(
            plan.fallback.as_ref().map(|event| event.code.as_str()),
            Some("reserved_override")
        );
        assert_eq!(plan.environment, request.base_environment);
        fs::remove_dir_all(root).expect("cleanup");
    }

    #[test]
    fn target_module_override_is_reserved() {
        let root = temp_dir("reserved-target-module");
        let mut request = request(&root);
        request.overrides.insert(
            "TOPAZ_SLP_TARGET_MODULE_NAME".to_owned(),
            "models.other.module".to_owned(),
        );
        let plan = plan_launch(&request);
        assert_eq!(plan.mode, LaunchMode::NativeFallback);
        assert_eq!(
            plan.fallback.as_ref().map(|event| event.code.as_str()),
            Some("reserved_override")
        );
        assert_eq!(plan.environment, request.base_environment);
        fs::remove_dir_all(root).expect("cleanup");
    }
}
