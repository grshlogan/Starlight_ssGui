pub mod injection;
pub mod log_parser;
pub mod protocol;

pub use injection::{
    FallbackEvent, InjectionEnvironment, InjectionError, InjectionRequest, LaunchMode, LaunchPlan,
    assemble_environment, plan_launch,
};
pub use log_parser::{
    ChunkProgress, Dialect, LogEvent, LogParser, ParseSummary, Phase, detect_module_dialect,
};
pub use protocol::{ControlCommand, MessageKind, StructuredError, StructuredEvent};
