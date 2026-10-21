use std::fmt;

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Phase {
    VaeEncode,
    DitUpscale,
    VaeDecode,
}

impl Phase {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::VaeEncode => "VAE Encode",
            Self::DitUpscale => "DiT Upscale",
            Self::VaeDecode => "VAE Decode",
        }
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub enum Dialect {
    Version170,
    Version171,
    ContractMatched,
    Unknown(String),
}

#[derive(Clone, Debug, PartialEq)]
pub struct ChunkProgress {
    pub chunk_index: Option<u32>,
    pub chunk_total: Option<u32>,
    pub progress_percent: Option<f32>,
}

#[derive(Clone, Debug, PartialEq)]
pub enum LogEvent {
    Version {
        version: String,
        dialect: Dialect,
    },
    Phase(Phase),
    Progress {
        phase: Option<Phase>,
        value: ChunkProgress,
    },
    Completed {
        seconds: Option<f64>,
    },
    Unknown {
        line: String,
    },
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct ParseSummary {
    pub events: Vec<LogEvent>,
    pub unknown_count: usize,
    pub version: Option<String>,
    pub completed_seconds: Option<f64>,
}

#[derive(Clone, Debug, Default)]
pub struct LogParser {
    summary: ParseSummary,
    current_phase: Option<Phase>,
    module_name: Option<String>,
}

impl LogParser {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn set_module(&mut self, module_name: impl Into<String>) {
        self.module_name = Some(module_name.into());
    }

    pub fn feed_line(&mut self, line: &str) -> LogEvent {
        let event = parse_line(line, self.module_name.as_deref());
        match &event {
            LogEvent::Version { version, .. } => self.summary.version = Some(version.clone()),
            LogEvent::Phase(phase) => self.current_phase = Some(phase.clone()),
            LogEvent::Progress { phase, .. } => {
                if let Some(phase) = phase {
                    self.current_phase = Some(phase.clone());
                }
            }
            LogEvent::Completed { seconds } => {
                if let Some(seconds) = seconds {
                    self.summary.completed_seconds = Some(*seconds);
                }
            }
            LogEvent::Unknown { .. } => self.summary.unknown_count += 1,
        }
        self.summary.events.push(event.clone());
        event
    }

    pub fn finish(self) -> ParseSummary {
        self.summary
    }
}

pub fn parse_lines(lines: impl IntoIterator<Item = impl AsRef<str>>) -> ParseSummary {
    let mut parser = LogParser::new();
    for line in lines {
        parser.feed_line(line.as_ref());
    }
    parser.finish()
}

pub fn detect_module_dialect(version: &str, module_name: &str, contract_match: bool) -> Dialect {
    if version == "1.7.0" && module_name == "models.slp25.m0vm5nn8kicb" {
        return Dialect::Version170;
    }
    if version == "1.7.1" && module_name == "models.slp25.rx095brph7m1" {
        return Dialect::Version171;
    }
    if contract_match && module_name.starts_with("models.slp2") {
        return Dialect::ContractMatched;
    }
    Dialect::Unknown(version.to_owned())
}

fn module_contract_matches(module_name: &str) -> bool {
    // The reference contract uses the models.slp2 namespace and the hook checks
    // PIX_CHUNK_SIZE/VAE_DECODE_TILE_SIZE before applying changes. The parser
    // uses the same namespace contract for unknown versions; it does not rely on
    // the version-specific hash table below.
    module_name.starts_with("models.slp2")
}

fn detect_phase(line: &str) -> Option<Phase> {
    if line.contains("VAE Encode") {
        Some(Phase::VaeEncode)
    } else if line.contains("DiT Upscale") {
        Some(Phase::DitUpscale)
    } else if line.contains("VAE Decode") {
        Some(Phase::VaeDecode)
    } else {
        None
    }
}

fn parse_number<T: std::str::FromStr>(value: &str) -> Option<T> {
    value
        .trim_matches(|character: char| {
            !character.is_ascii_digit() && character != '.' && character != '-'
        })
        .parse()
        .ok()
}

const TOTAL_PROCESSING_TIME_MARKER: &str = "total processing time:";

fn parse_chunk(line: &str) -> (Option<u32>, Option<u32>) {
    let lower = line.to_ascii_lowercase();
    let start = lower.find("chunk").map(|index| index + "chunk".len());
    let Some(start) = start else {
        return (None, None);
    };
    let tail = &line[start..];
    let slash = tail.find('/');
    if let Some(slash) = slash {
        let left = tail[..slash]
            .split_whitespace()
            .next_back()
            .and_then(parse_number::<u32>);
        let right = tail[slash + 1..]
            .split_whitespace()
            .next()
            .and_then(parse_number::<u32>);
        return match (left, right) {
            (Some(left), Some(right)) => (Some(left), Some(right)),
            _ => (None, None),
        };
    }
    (None, None)
}

fn parse_progress(line: &str) -> Option<f32> {
    let lower = line.to_ascii_lowercase();
    let percent = lower.find('%')?;
    let before = &line[..percent];
    let value = before.split_whitespace().next_back()?;
    parse_number::<f32>(value)
}

fn parse_seconds(line: &str) -> Option<f64> {
    let start = line
        .to_ascii_lowercase()
        .find(TOTAL_PROCESSING_TIME_MARKER)?
        + TOTAL_PROCESSING_TIME_MARKER.len();
    let seconds = line[start..].trim().trim_end_matches('s').trim();
    parse_number(seconds)
}

fn parse_version(line: &str) -> Option<String> {
    let marker = "Setup logging for Topaz Video ";
    let start = line.find(marker)? + marker.len();
    let version = line[start..]
        .split_whitespace()
        .next()?
        .trim_matches(|character: char| !character.is_ascii_digit() && character != '.')
        .to_owned();
    (!version.is_empty()).then_some(version)
}

pub fn parse_line(line: &str, module_name: Option<&str>) -> LogEvent {
    let clean = line.trim_end_matches(['\r', '\n']);
    if clean.is_empty() {
        return LogEvent::Unknown {
            line: clean.to_owned(),
        };
    }
    if let Some(version) = parse_version(clean) {
        let dialect = module_name
            .map(|module| detect_module_dialect(&version, module, module_contract_matches(module)))
            .unwrap_or_else(|| Dialect::Unknown(version.clone()));
        return LogEvent::Version { version, dialect };
    }
    let lower = clean.to_ascii_lowercase();
    if let Some(seconds) = parse_seconds(clean) {
        return LogEvent::Completed {
            seconds: Some(seconds),
        };
    }
    if lower.contains(TOTAL_PROCESSING_TIME_MARKER) {
        return LogEvent::Unknown {
            line: clean.to_owned(),
        };
    }

    let phase = detect_phase(clean);
    let (chunk_index, chunk_total) = parse_chunk(clean);
    let progress_percent =
        if lower.contains("chunk") && chunk_index.is_none() && chunk_total.is_none() {
            None
        } else {
            parse_progress(clean)
        };
    if chunk_index.is_some() || chunk_total.is_some() || progress_percent.is_some() {
        return LogEvent::Progress {
            phase,
            value: ChunkProgress {
                chunk_index,
                chunk_total,
                progress_percent,
            },
        };
    }
    if let Some(phase) = phase {
        return LogEvent::Phase(phase);
    }
    LogEvent::Unknown {
        line: clean.to_owned(),
    }
}

impl fmt::Display for Phase {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.as_str())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_phases_progress_and_completion() {
        let summary = parse_lines([
            "2026-10-19 10-00-00.000 Thread: 1 Info VAE Encode",
            "2026-10-19 10-00-01.000 Thread: 1 Info DiT Upscale chunk 2/8 progress 25%",
            "2026-10-19 10-00-02.000 Thread: 1 Info VAE Decode",
            "2026-10-19 10-00-03.000 Thread: 1 Info total processing time: 3.5s",
        ]);
        assert_eq!(summary.unknown_count, 0);
        assert_eq!(summary.completed_seconds, Some(3.5));
        assert!(summary.events.contains(&LogEvent::Phase(Phase::VaeEncode)));
        assert!(summary.events.contains(&LogEvent::Progress {
            phase: Some(Phase::DitUpscale),
            value: ChunkProgress {
                chunk_index: Some(2),
                chunk_total: Some(8),
                progress_percent: Some(25.0),
            },
        }));
    }

    #[test]
    fn parses_checked_in_fixtures() {
        let first = parse_lines(include_str!("../../fixtures/tzlog/1.7.0.tzlog").lines());
        let second = parse_lines(include_str!("../../fixtures/tzlog/1.7.1.tzlog").lines());
        assert_eq!(first.version.as_deref(), Some("1.7.0"));
        assert_eq!(second.version.as_deref(), Some("1.7.1"));
        assert_eq!(first.completed_seconds, Some(5.0));
        assert_eq!(second.completed_seconds, Some(4.0));
        assert_eq!(first.unknown_count, 0);
        assert_eq!(second.unknown_count, 1);
        assert!(first.events.contains(&LogEvent::Phase(Phase::VaeEncode)));
        assert!(first.events.iter().any(|event| matches!(
            event,
            LogEvent::Progress {
                phase: Some(Phase::DitUpscale),
                ..
            }
        )));
        assert!(first.events.contains(&LogEvent::Phase(Phase::VaeDecode)));
        assert!(second.events.iter().any(|event| matches!(
            event,
            LogEvent::Progress {
                phase: Some(Phase::VaeEncode),
                ..
            }
        )));
        assert!(second.events.iter().any(|event| matches!(
            event,
            LogEvent::Progress {
                phase: Some(Phase::DitUpscale),
                ..
            }
        )));
        assert!(second.events.contains(&LogEvent::Phase(Phase::VaeDecode)));
        let first_progress: Vec<_> = first
            .events
            .iter()
            .filter_map(|event| match event {
                LogEvent::Progress { value, .. } => {
                    Some((value.chunk_index, value.chunk_total, value.progress_percent))
                }
                _ => None,
            })
            .collect();
        let second_progress: Vec<_> = second
            .events
            .iter()
            .filter_map(|event| match event {
                LogEvent::Progress { value, .. } => {
                    Some((value.chunk_index, value.chunk_total, value.progress_percent))
                }
                _ => None,
            })
            .collect();
        assert_eq!(
            first_progress,
            vec![
                (Some(1), Some(3), Some(33.0)),
                (Some(2), Some(3), Some(66.0))
            ]
        );
        assert_eq!(
            second_progress,
            vec![
                (Some(1), Some(2), Some(50.0)),
                (Some(2), Some(2), Some(100.0))
            ]
        );
    }

    #[test]
    fn chunk_like_lines_without_chunk_pair_are_unknown() {
        let summary = parse_lines([
            "2026-10-19 10-00-00.000 Warn chunk size must be at least 256",
            "2026-10-19 10-00-01.000 Info unrelated chunk 2 progress 50%",
        ]);
        assert_eq!(summary.unknown_count, 2);
        assert!(
            summary
                .events
                .iter()
                .all(|event| matches!(event, LogEvent::Unknown { .. }))
        );
    }

    #[test]
    fn completion_requires_a_parsed_duration() {
        for line in [
            "2026-10-19 10-00-03.000 Info total processing time: unknown",
            "2026-10-19 10-00-03.000 Info total processing time: ",
            "2026-10-19 10-00-03.000 Info total processing time: 3,5s",
        ] {
            assert!(matches!(parse_line(line, None), LogEvent::Unknown { .. }));
        }
        assert!(matches!(
            parse_line(
                "2026-10-19 10-00-03.000 Info total processing time 3.5s",
                None
            ),
            LogEvent::Unknown { .. }
        ));
        assert_eq!(
            parse_line(
                "2026-10-19 10-00-03.000 Info total processing time: 3.5s",
                None
            ),
            LogEvent::Completed { seconds: Some(3.5) }
        );
    }

    #[test]
    fn completion_without_a_parsed_duration_does_not_clear_summary() {
        let summary = parse_lines([
            "2026-10-19 10-00-03.000 Info total processing time: 3.5s",
            "2026-10-19 10-00-04.000 Info total processing time: unknown",
        ]);
        assert_eq!(summary.completed_seconds, Some(3.5));
        assert_eq!(summary.unknown_count, 1);
    }

    #[test]
    fn unknown_and_truncated_lines_are_counted_without_failure() {
        let summary = parse_lines([
            "2026-10-19 10-00-00.000 Thread: 1 Info unrelated line",
            "2026-10-19 10-00",
            "",
        ]);
        assert_eq!(summary.unknown_count, 3);
        assert_eq!(summary.completed_seconds, None);
    }

    #[test]
    fn parser_recognizes_all_dialects_through_log_parser() {
        let cases = [
            ("1.7.0", "models.slp25.m0vm5nn8kicb", Dialect::Version170),
            ("1.7.1", "models.slp25.rx095brph7m1", Dialect::Version171),
            ("1.7.9", "models.slp25.future", Dialect::ContractMatched),
            (
                "1.7.9",
                "models.other.module",
                Dialect::Unknown("1.7.9".to_owned()),
            ),
        ];
        for (version, module, expected_dialect) in cases {
            let mut parser = LogParser::new();
            parser.set_module(module);
            assert_eq!(
                parser.feed_line(&format!(
                    "2026-10-21 10-00-00.000 Setup logging for Topaz Video {version}"
                )),
                LogEvent::Version {
                    version: version.to_owned(),
                    dialect: expected_dialect,
                }
            );
        }
    }
}
