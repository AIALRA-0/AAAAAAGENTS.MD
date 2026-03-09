---
last_updated: 2026-03-08-22-00
---

# SHELL_SCRIPT STANDARD

## Basic requirements
- all `Shell` The script must use `UTF-8` coding
- All scripts must declare an explicit interpreter,For example `#!/usr/bin/env bash` or `#!/bin/sh`
- Script interpreters within the same project must be consistent,It is prohibited to mix unspecified `bash` and `sh`
- Before writing a script, the target operating environment must be clear,For example `Linux`,`macOS`,`BusyBox`,`CI Runner`
- Scripts must prioritize readability,Maintainability,Auditability and rollback
- It is forbidden to use excessive technical writing in order to compress the number of lines.
- It is forbidden to accumulate complex business logic in scripts for a long time,Complex logic should be migrated to a more appropriate language implementation

## Interpreter and compatibility
- use `bash` Characteristics,Must be explicitly declared `bash` interpreter
- use `sh` hour,prohibited from introduction `bash` Exclusive syntax
- It must not be assumed by default that all environments support arrays,associative array,`[[ ... ]]`,Advanced capabilities such as process replacement
- When cross-platform execution is required,Must avoid relying on platform-specific command behavior
- involving `sed`,`awk`,`grep`,`xargs`,`find` While waiting for tools,Implementation differences between different systems must be considered
- When there are requirements for the system command version,Preconditions must be stated in the script header or description
- Scripts must minimize implicit dependencies on external environment state

## File header and script structure
- Every script should contain a clear header description
- The file header suggests the purpose of the script,input parameters,Output results,Depend on command,Implementation examples and risk warnings
- The main process must be clearly segmented,Disable unstructured stacking of large numbers of commands
- initialization,Parameter analysis,check,main logic,clean up,Exit must be separated from the organization as much as possible
- The script entry must be clear,Recommended to use `main` Unified function scheduling
- It is forbidden to execute a large amount of logic directly on the top level of the file.
- Script structure must allow readers to quickly identify execution sequences and failure paths

## Security options
- `bash` Scripts should use strict mode by default,For example `set -euo pipefail`
- right `IFS` When requested,Must be set explicitly and explain why
- It is forbidden to turn off strict mode without understanding the scope of the impact.
- Need to be partially closed `set -e` or similar options,Must narrow down the scope and write down the reasons clearly
- The failure behavior of pipe commands must be explicitly controlled,Avoid preorder failures from being swallowed silently
- Commands that are allowed to fail must be handled explicitly,Instead of relying on default behavior to muddle through

## Naming convention
- Script file names should be clear and stable `kebab-case` Or project unified naming style
- Variable names should always use all-capital constant style or lowercase underline style.,And the same project remains consistent
- Environment variables and read-only constants are recommended `UPPER_SNAKE_CASE`
- It is recommended to use local ordinary variables `lower_snake_case`
- Function names must express action semantics,Recommended to use `lower_snake_case`
- Naming must be semantically clear,Prohibited use `tmp`,`foo`,`bar`,`data2` Such names without business meaning
- Boolean semantic variables should use readable naming,For example `is_dry_run`,`has_error`,`should_retry`

## Variable usage
- All variables must be quoted with double quotes by default,For example `"$var"`
- Disallow unquoted variable expansion without confirming safety
- path,file name,Command parameters,User input must be treated as if it may contain spaces and special characters
- Variables must be defined before they can be used
- Required environment variables must be explicitly verified
- Optional variables must provide sensible default values
- Propagating state by relying on undeclared global variables is prohibited
- This should be used in preference when using command substitution `$(...)`,The use of backticks is prohibited
- Variable scope must be as narrow as possible,Local variables are used first `local`
- Constants must be defined only once,It is prohibited to be implicitly rewritten in subsequent processes.

## function specification
- Logic in a script that exceeds a simple linear command flow must be split into functions
- Each function must have a single responsibility
- Functions should be as short as possible,Avoid deep nesting and multiple side effects
- Function inputs should be passed in explicitly via parameters,Disallow reliance on implicit external state
- Function return codes must have clear semantics
- When you need to return string content,should be returned via standard output,And strictly distinguish it from the log output
- For complex functions, it is recommended to briefly describe the purpose at the beginning,enter,Output and failure conditions
- Functions must not quietly modify global state that is difficult for the caller to perceive

## Annotation specifications
- Comments must explain why,constraint,risk,Compatibility and non-intuitive points,Instead of repeating the literal meaning of the command
- Simple and straightforward commands without repetitive nonsense comments
- dependence on external,boundary conditions,Dangerous operation,Fallback on failure,Temporary compatible writing must be clearly annotated
- Comments must be in sync with script behavior,Expired comments must be deleted or updated promptly
- Emotional use is prohibited,colloquial,Personalized notes
- `TODO`,`FIXME`,`HACK` Reasons and follow-up directions must be provided
- File header comments should give priority to helping users understand how to execute and how to troubleshoot

## Parameter analysis
- All scripts intended for reuse or automation calls must support `--help`
- Parameter names must be clear,Stablize,Predictable
- Short parameter and long parameter styles must be consistent
- When parameter parsing fails, clear error messages and help prompts must be output
- When required parameters are missing, you must fail and exit immediately.
- Parameter defaults must be safe,keep,explainable
- Not allowed silently Ignore unknown parameters
- When there are restrictions on multi-parameter combinations,Conflict relationships must be explicitly verified
- support `dry-run` The script should be provided first `--dry-run` Options

## Input and output
- Script input must be explicitly validated,External incoming content must not be directly trusted
- Key output must be readable,parsable,auditable
- Output to automated systems should be in stable text format or structured format whenever possible.
- Standard output is applied to the resulting output,Standard error should be used for error messages and diagnostic information
- Disallow mixing debug information with formal results in the same output stream
- Output copy must be concise and clear,Avoid uninformative nonsense
- Sufficient context should be provided for key steps,Easy to locate failure location

## Error handling
- Read and write all files,Directory operations,network request,External command calls must consider the failure path
- Error messages must contain sufficient context,For example target path,Order,parameter,stage information
- Disable ignoring return codes
- For commands that allow failure, the reasons for failure and subsequent processing logic must be clearly stated.
- Whether to retry after failure,jump over,rollback or abort,Must behave clearly
- Exceptions that can be automatically repaired must be deterministically repaired
- Non-deterministic problems must not be disguised as success
- Exit codes must have clear semantics,Return successfully `0`,Return non-zero code on failure
- Different exit codes can be used for different types of failures.,But there must be an explanation

## Log specifications
- The script must provide a unified log output method
- It is recommended that the log level be at least differentiated `info`,`warn`,`error`
- Logs should contain key context,For example, step name,target audience,command result
- It is prohibited to use randomly scattered `echo` As a formal log scheme
- The high frequency path must not output noise logs
- Error logs must help locate problems quickly
- Passwords must not be revealed in the logs,token,key,Sensitive information such as private data
- Long process scripts should output key stage start and end markers
- When machine consumption logs are needed,A stable prefix or structured output format should be provided

## External command call
- Before calling an external command, you must confirm that the command exists,Perform dependency checks first if necessary
- Command parameters must be quoted correctly,Prevent whitespace splitting and injection risks
- It is prohibited to directly splice unverified user input into commands.
- Batch command execution must have a clear failure strategy
- right `rm`,`mv`,`cp`,`chmod`,`chown`,`find -exec` Be extremely cautious when waiting for dangerous orders
- Explicit protection should be provided before performing destructive operations,For example confirm,whitelist,prefix checkor `dry-run`
- Targets must be logged when remote command execution is involved,Command scope and failure fallback strategy
- involving `sudo` You must minimize the scope of permissions and write down the reasons clearly

## Path and file handling
- All path processing must take spaces into account,wildcard,Line breaks and special character risks
- Absolute paths or normalized relative paths must be used in preference
- Temporary files must be placed in an explicit temporary directory
- Temporary files and temporary directories must be cleaned up on exit
- Important file writes should preferentially use the atomic write strategy
- The intention to overwrite must be clear before overwriting a file
- Before deleting, you must confirm that the target path is legal.,Disable dangerous deletion of empty variables or root path class targets
- When the directory does not exist, you should specify whether to create it automatically or exit with an error.
- File reading and writing encoding,Line wrapping and permission requirements must be controlled explicitly where necessary

## Clean up and exit
- Involves temporary resources,lock file,background process,mount point,When switching working directories,Cleanup logic must be provided
- Cleanup logic suggestion passed `trap` Unified registration
- `trap` The operations in must be repeatable and as safe as possible
- Must ensure that the key status is consistent before exiting,Avoid half-finished status from polluting the environment
- interrupt,fail,The three types of exit paths that end normally must be as controllable as possible
- Rolling back costly operations,Priority must be given to designing pre-inspection mechanisms rather than post-mortem remediation

## Idempotence and repeatable execution
- Repeatable scripts must be designed to be idempotent as much as possible
- Resource already exists,Completed steps,Repeated calls to the scene must have clear behavior
- It must not produce uncontrollable side effects when executed repeatedly.
- The initialization class script must indicate whether repeated execution is allowed
- The update class script must indicate whether to overwrite,Merge or skip existing states
- Idempotent logic must preferably be implemented via explicit checks,rather than relying on chance success

## security requirements
- Disallow hard-coded passwords,key,Tokens and sensitive credentials
- Sensitive parameters are passed through environment variables first,Credentials file or secure injection method delivery
- log,Sensitive information must not be leaked in error reports and debugging output
- user input,External file content,Environment variables must be treated as untrusted input
- any download,implement,Unzip,cover,Deletion actions must consider the risk of input contamination
- After downloading remote resources,The checksum must be verified if necessary,Signature or source credibility
- Involves privilege escalation,System configuration modification,The scope of impact must be minimized when services are started or stopped.
- Default behavior must be safe,Dangerous abilities must be explicitly enabled

## Maintainability
- Common logic should be extracted as public functions,Avoid copy-pasting
- Parameter style for similar scripts,log style,The exit code style must be consistent
- Complex scripts must provide example usage
- The script directory structure within the project should be clear and stable,Easy to discover and reuse
- Major changes must be implemented step by step first,Avoid rewriting the entire script at once
- Technical debt must be visible,Temporary compatibility logic must not be hidden for a long time
- Important scripts should have minimum self-checking capabilities,For example dependency checking,environmental inspection,Permission check

## Testing and verification
- All non-disposable scripts should provide at least a minimum executable verification path
- Key scripts should have `lint`,Syntax checking or minimal integration testing
- `bash` Script suggestion passed `shellcheck` examine
- Recommend execution before submission `bash -n` or equivalent syntax check
- Key processes should cover the path to success,Failure paths and boundary paths
- Testing must not contaminate the real production environment
- Scripts involving external systems should preferably provide a simulation environment or `dry-run`
- Important output must be predictable,Avoid test results relying on random environment states

## Performance and resource usage
- Scripts must avoid meaningless repeated calls to costly external commands
- Batch processing must take precedence over streaming or batch processing
- The obviously inefficient per-file subprocess abuse method must not be used in large-scale file scenarios.
- The number of child processes should be reduced in high-frequency loops
- Should be used wisely when processing large amounts of text `awk`,`sed`,`grep` and other tools,But readability must be taken into account
- Performance optimization must be based on clear bottlenecks,instead of guessing

## Prohibited matters
- Disable undeclared interpreters
- Disable ignoring return codes of critical commands
- Disable unquoted expansion of untrusted variables
- Direct splicing of untrusted input to execute commands is prohibited
- Prohibition of missing bounds checks before dangerous operations
- Hardcoding sensitive information in scripts is prohibited
- Overly complex and difficult-to-maintain one-line writing is prohibited
- It is forbidden to use syntax that is incompatible with the interpreter
- Disable formal output,Log output and error output are mixed together
- It is forbidden to pile up complex business logic into untestable long scripts for a long time.