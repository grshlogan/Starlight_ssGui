use std::collections::BTreeMap;

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum MessageKind {
    ControlCommand,
    StateSnapshot,
    StructuredEvent,
    StructuredError,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum ControlCommand {
    Start,
    Stop,
    Cancel,
    Refresh,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct StructuredEvent {
    pub event: String,
    pub launch_id: String,
    pub changes: BTreeMap<String, String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct StructuredError {
    pub code: String,
    pub message: String,
    pub recoverable: bool,
}

impl MessageKind {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::ControlCommand => "control_command",
            Self::StateSnapshot => "state_snapshot",
            Self::StructuredEvent => "structured_event",
            Self::StructuredError => "structured_error",
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn seam_kinds_are_explicit_and_small() {
        assert_eq!(MessageKind::ControlCommand.as_str(), "control_command");
        assert_eq!(MessageKind::StateSnapshot.as_str(), "state_snapshot");
        assert_eq!(MessageKind::StructuredEvent.as_str(), "structured_event");
        assert_eq!(MessageKind::StructuredError.as_str(), "structured_error");
    }
}
