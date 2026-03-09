---
last_updated: 2026-03-08-15-50
---

# BATCH STANDARD

## Basic requirements
- all `BAT` The file must use `UTF-8` coding,and ensure that the target execution environment correctly recognizes the encoding;
- All scripts must be readable as a priority,Maintainability,Auditability and rollback;
- Script styles in the same project,variable style,error handling style,Logging style must be consistent;
- Disable stacking of unreadable single-line commands to save trouble;
- It is forbidden to introduce complex techniques that are irrelevant to current needs;
- All scripts must be in Windows Can be run in a standard command interpreter environment;
- If the script depends on a specific system version,Specific toolchain or specific environment variables,must be stated explicitly;

## Documentation and structural requirements
- All scripts must end with `@echo off` beginning;
- It is recommended to use it at the beginning `setlocal` Control variable scope;
- If the script uses delayed expansion,Must be used explicitly `setlocal EnableDelayedExpansion`;
- The script must begin with a description of the purpose of the script;
- The main structure of the script must be clear,initialization,Parameter analysis,core process,Cleaning up and closing should have clear boundaries;
- Complex scripts should be split into multiple tag segments,For example `:main`,`:parse_args`,`:cleanup`;
- Tag naming must be semantically clear,Meaningless short names are prohibited;
- The script must end by explicitly `exit /b` return exit code;
- Disallow relying on the natural end of a command as a formal exit method;

## Naming convention
- Environment variable naming must be semantically clear;
- It is recommended to use a unified prefix for project-level variables,Avoid conflicts with system variables;
- It is recommended to use all uppercase and underline style for variable names.,For example `OUTPUT_DIR`,`EXIT_CODE`;
- Temporary variables must reflect their purpose,Prohibited use `a`,`b`,`tmp1`,`xx` Such semantic-less names;
- Tag names must reflect actions or responsibilities,For example `:copy_files`,`:validate_input`;
- Boolean semantic variables must be as clear as possible,For example `HAS_ERROR`,`DRY_RUN`,`VERBOSE_MODE`;

## Annotation specifications
- Comments must explain why,boundary,Constraints and non-intuitive behavior,Rather than repeating the surface meaning of the command;
- Simple and straightforward commands must not force repetitive comments to be added.;
- For complex jumps,Parameter constraints,external dependencies,Dangerous operation,Failure fallback must be clearly commented;
- Annotations must be kept in sync with the script implementation;
- Expired comments must be deleted or updated promptly;
- It is forbidden to write uninformative comments,For example"Set variables""execute command";
- Emotional use is prohibited,Colloquial or personalized comments;
- Temporary instructions should use unified markup,For example `REM TODO:`,`REM FIXME:`,with clear reasons;

## coding style
- A command only performs a clear action;
- Complex logic must be broken into multiple steps,Cannot stack to form long chain commands;
- Conditional judgment,cycle,Jumps must be as shallowly nested as possible;
- Abuse prohibited `goto` Create an untraceable process;
- Tags and `call` organizational process,But it must be ensured that the calling path is clear;
- Core processes must be traceable,Debuggable,Targetable;
- Condition checks must be done explicitly before dangerous commands;
- The same logic must be extracted and reused,Copying and pasting large sections is prohibited;
- Command writing style must be consistent,For example, use unified `if not exist` Or use positive judgment uniformly;
- Path with spaces,Handling of arguments with special characters must always be consistent;

## Variables and extensions
- All variable assignments must be done using `set "KEY=value"` style;
- Nude is prohibited `set KEY=value` to avoid trailing spaces and special characters issues;
- When you need to read dynamic variables in a loop or code block,Delayed expansion must be used explicitly;
- Care must be taken when using delayed expansion `!` Content corruption issues caused by characters;
- Do not use confusingly in scripts `%VAR%` and `!VAR!`;
- Variable scope must be clear,Avoid unintentional pollution of the calling environment;
- Temporary variables should be cleaned up promptly after use or limited to `setlocal` within life cycle;
- Important variables must be initialized before use;

## Parameter handling
- Scripts must clearly define supported parameter formats;
- Command line parameters must provide a help entry,For example support `-h`,`--help`,`/help` one or more of;
- Parameter names and behavior must be stable,Disable implicit drift;
- Parameter parsing logic must be centralized,Avoid being scattered in the main process;
- When required parameters are missing, a non-zero exit code must be returned and a clear error message must be output.;
- Optional parameters must have explicit default values;
- Unrecognized parameters must be reported explicitly.,Not to be ignored in silence;
- If the parameter value involves a path,model,environment name,Identification name, etc.,Legality verification is required;
- Boolean parameters must have a consistent style,For example, uniformly adopt `--dry-run` or `/dryrun` style;

## Path and file handling
- All path processing must consider the space path situation;
- Path variables must always be wrapped in quotes when used;
- Path splicing must be clear and stable,Disallow reliance on fragile string concatenation;
- File reading and writing,copy,move,Target existence and expected state must be checked before deletion;
- Overwriting behavior must be explicit when it comes to overwriting writes;
- Protection conditions must be added when deletion operations are involved,Avoid accidental deletion;
- Temporary files and temporary directories must have a clear life cycle;
- Cross drive letter operation,Relative path resolution and changes to the current working directory must be handled with caution;
- If the script depends on the directory where it is located,Must use `%~dp0` or equivalently explicit positioning;
- Disable the assumption that scripts are always executed in a fixed working directory;

## Error handling
- Critical commands must be explicitly checked for failure status after execution;
- The critical path must be checked `errorlevel` or equivalent failure signal;
- It is prohibited to continue to perform subsequent high-risk steps unconditionally after a failure.;
- Error messages must contain sufficient context,At least describe the failed action and target object;
- Disable swallowing errors without outputting any information;
- Deterministically repairable failures should be clearly distinguished as deterministically repairable;
- Non-deterministic failure must not be disguised as success;
- to external commands,File system operations,network access,Dependent tool calls must explicitly handle failed branches;
- All failed exits must return a non-zero exit code;
- Success paths must be returned explicitly `0`;

## Logs and output
- Script output must clearly differentiate between normal information,Warning and error messages;
- Critical steps must have readable log output;
- Log content must be concise and clear,Avoid meaningless noise output;
- Error logs must help locate problems quickly;
- When it comes to automation integration,Important output should be as structured as possible or at least in a stable format;
- It is forbidden to rely entirely on debug output for official logs;
- In batch loop processing,Log granularity must be moderate,Avoid swiping;
- success,fail,jump over,It is recommended to use a unified prefix for retry and other states.;
- Sensitive information must not be revealed in the output,For example password,token,key,Internal address credentials etc.;

## process control
- The entrance to the main process must be clear,It is recommended to explicitly jump to `:main`;
- Initialization logic must be completed before the main process;
- Parameter analysis,Environment verification,core execution,Cleaning up and finishing should keep the order clear;
- all `goto` Jump targets must be clear and limited;
- It is forbidden to construct complex and unreadable multi-layer jump networks;
- Public logic recommendation passed `call :label` Mode reuse;
- Subprocesses must maintain calling boundaries by explicitly returning;
- Cleanup logic must be executable in both success and failure paths;

## External commands and dependencies
- Before calling all external commands, you must confirm that dependencies exist.;
- A clear prompt must be output when a dependency is missing.;
- If the external command path is not available by default in the system,Must be configured explicitly;
- External command calls must check return codes;
- When command calls involve parameter splicing, special characters must be prevented from being damaged.;
- If the script depends on `PowerShell`,`Python`,`Git`,`7z` and other tools,The minimum acceptable environment must be stated;
- Calling high-risk commands,Pre-checksum failure fallback must be added;

## Compatibility requirements
- The script must specify the target adaptation Windows environmental scope;
- Different system locales,coding environment,Differences in command interpretation must be considered in advance;
- Involves Chinese path,Space path,Special character paths must be tested when;
- Use delayed expansion,pipeline,Redirect,Must be considered when nesting loops `cmd` Feature differences;
- If a certain writing method is only applicable to a specific version of the system or shell behavior,Must be explicitly noted;
- Disable the default assumption that the execution environment is exactly the same;

## security requirements
- Disallow hard-coded passwords,token,Keys and sensitive credentials;
- delete,cover,move,Destructive operations such as formatting must be explicitly controlled;
- Involving system directories,user directory,Environment variables must be modified with caution;
- Necessary verification must be done when inputting splicing commands from outside;
- Unprotected execution of commands formed by user-controllable input is prohibited;
- Sensitive information must not be revealed in logs and error output;
- Default behavior must be safe,Ask for explicit confirmation when necessary;
- Danger mode suggestions are added `dry-run` or preview ability;

## Testing and verification
- Each script should provide at least a minimal executable verification path;
- Key scripts must have minimum success path and failure path verification;
- Parameter missing,path does not exist,Missing dependencies,Scenarios such as command failure must be testable;
- Critical commands must support non-zero exit codes;
- Important output format must be stable,Convenient automated consumption;
- Regression problems should be supplemented with corresponding test samples or minimum reproducible use cases.;
- Tests must not rely on uncontrollable external state;
- There must be separation of duties between production scripts and test scripts;

## Maintainability requirements
- Script responsibility must be single,Scripts that are too large must be split;
- Common logic should be precipitated into reusable subscripts or tag segments;
- The scope of influence must be controlled when modifying the script;
- Major changes must be implemented in steps,Avoid introducing a lot of uncertainty at once;
- All key implementations should be targetable,Can be rolled back,auditable;
- Temporary compatibility code must be accompanied by a cleanup plan;
- Technical debt must be visible,Must not be hidden in complex jumps and magic variables;
- Long-term maintenance script,Instructions for use and parameter description must be provided;

## Prohibited matters
- Missing prohibited `@echo off`;
- No nudity `set KEY=value`;
- It is forbidden to use unquoted paths that may contain spaces.;
- Prohibited without checking `errorlevel` Just continue with the key steps;
- Disable null error handling;
- Disable swallowing failure status;
- Disable reliance on implicit current directory;
- Abuse prohibited `goto` Manufacturing unmaintainable processes;
- Hard coding of sensitive information is prohibited;
- Unprotected execution of high-risk delete or overwrite commands is prohibited;
- Disable long-term retention of debugging code,Temporarily skip logic and invalid comments;