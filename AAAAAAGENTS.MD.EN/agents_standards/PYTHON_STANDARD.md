---
last_updated: 2026-03-08-15-50
---

# PYTHON STANDARD

## Basic requirements
- all Python The file must use `UTF-8` coding;
- Used by default `Python 3.10+` grammatical properties,You must ensure that the project operating environment explicitly supports;
- All code must be readable as a priority,Maintainability and testability;
- Coding style in the same project,naming style,Abnormal style,Logging style must be consistent;
- It is forbidden to use unnecessary advanced syntax just to show off your skills.;
- It is forbidden to introduce complex abstractions that are irrelevant to current needs;
- Code implementation must prioritize the pursuit of clarity,Consider premature optimization again;

## coding style
- Follow by default `PEP 8`;
- Line width should remain stable,It is recommended not to exceed `88` Or the maximum length agreed upon by the project;
- Functions should be as short as possible,A single function has only one clear responsibility;
- Complex processes must be split into multiple small functions,Multiple responsibilities must not be stacked in a function;
- conditional branch,cycle,Exception handling nesting levels must not be too deep;
- Prefer explicit writing,Avoid unreadable chained expressions;
- Avoid implicit side effects,Core processes must remain traceable;
- Abuse of global variables is prohibited;
- Disable execution of high side-effect logic during module import phase;
- All constants must be defined centrally,It is forbidden to scatter mana in the code;
- Repeated logic must be extracted and reused,No meaningless copying and pasting is allowed;

## Naming convention
- variable name,function name,Use module names uniformly `snake_case`;
- Use uniform class names `PascalCase`;
- Use constant names uniformly `UPPER_SNAKE_CASE`;
- Private helper functions or internal properties are prefixed with an underscore,For example `_internal_func`;
- Naming must be semantically clear,Prohibited use `tmp`,`foo`,`bar`,`data2`,`test1` Such names without business meaning;
- Boolean variables should be named in a way that directly conveys true and false semantics.,For example `is_enabled`,`has_error`,`can_retry`;
- gather,list,Names such as mappings should reflect plural or container semantics;
- Function names should reflect actions,Variable names should reflect the data;

## type annotation
- public function,public method,Core intrinsics must explicitly provide type annotations;
- Function parameters and return values ​​must be marked as completely as possible;
- Externally exposed interfaces must not omit the return type;
- Prefer using the standard library `typing` stable type expression in;
- Complex nested types should be simplified for readability via type aliases;
- When the return value structure is fixed,Prefer clear data structure definitions,rather than loose `dict`;
- Type annotations must serve readability,It is forbidden to pile up overly complex type expressions;
- Allows use in dynamic scenarios `Any`,But the scope must be controlled and the reasons must be explained;

## Function design
- Functions must have a single responsibility;
- The number of function parameters should be as concise as possible,Too many parameters must be packaged;
- Prefer explicit parameters,Avoid relying on implicit context;
- Parameters with default values ​​must be safe,Predictable default behavior;
- Disable the use of mutable objects as default parameters,For example `[]`,`{}`;
- Function return value must be stable,Types with excessively different semantics must not be returned in different branches;
- The input and output of external functions must be predictable;
- Core functions should try to keep side effects free or controllable;
- Function too long,Too many branches,When responsibilities are mixed, they must be separated;

## class design
- Only use classes if you really need to encapsulate state or behavior aggregation;
- Prioritize simple data bearing `dataclass` or equivalent lightweight structure;
- Classes must have clear boundaries of responsibilities,Forbidden god class;
- There must be a clear boundary between public properties and internal properties;
- Inheritance must be used with caution,Prefer composition over deep inheritance;
- abstract base class,Interface classes are only introduced when there is real reuse and constraint value;
- class method,static method,The use of instance methods must comply with responsibility semantics;
- Initialization logic should not be too complex,Complex initialization must be split;

## Annotation specifications
- Comments must explain why,constraint,Boundaries and non-intuitive points,Instead of reciting the surface meaning of the code;
- Simple and straightforward code must not be forced to add repetitive comments;
- for complex logic,special branch,external dependencies,boundary conditions,Failure fallback must be clearly written;
- Comments must be in sync with the code,Expired comments must be deleted or updated promptly;
- It is forbidden to write uninformative comments,For example"Assign a value to a variable""Loop through data";
- Emotional use is prohibited,colloquial,Personalized notes;
- Module header comments can be used to describe module responsibilities,Input, output and usage restrictions;
- Function comments should give priority to describing the purpose,Key parameters,Return value semantics and exception constraints;
- Temporary instructions may not be retained for a long time,`TODO`,`FIXME`,`HACK` Must bring the reason or follow-up direction;

## docstring
- External module,public class,Public function suggestions are provided `docstring`;
- `docstring` Functional purpose must be stated,Instead of line-by-line translation implementation;
- Functions with many parameters or complex behavior must explain the meaning of the parameters;
- When the semantics of the return value are not obvious, the return content must be stated.;
- Functions that throw important exceptions should describe the exception scenario;
- Docstring style should be consistent within the project,For example, uniformly adopt `Google` style or simplicity;
- Do not mix multiple completely different docstring styles in the same project;

## Import specification
- Import order must be stable,Usually by standard library,Third-party libraries,Local module grouping;
- Prohibited use `from xxx import *`;
- Disable unused imports;
- Circular dependencies must be avoided;
- Module paths must be clear,Disable fragile relative paths hack import;
- Import aliases are only used when shortening common and recognized names.;
- Module imports must remain declared at the top,Unless delayed import clearly solves performance or circular dependency issues;

## Data structures and models
- Fixed structure data preferentially uses explicit model definitions,For example `dataclass`,`TypedDict`,class object;
- Dynamic dictionaries are only used in loose scenarios where necessary;
- Field names must be stable,It is prohibited to mix the same concept with multiple key names.;
- Data structure levels must not be nested uncontrollably;
- Core structures must be serializable,Printable,Debuggable;
- External input data must be verified before use;
- Data models must reflect business semantics,Rather than just trying to save trouble;

## Error handling
- all `IO`,parse,network request,External command calls must handle exceptions explicitly;
- The error message must contain sufficient positioning context;
- Empty is prohibited `except`;
- It is forbidden to swallow exceptions directly without handling them.;
- When catching an exception, you must first catch the specific exception type.,instead of grabbing `Exception`;
- Exceptions that cannot be handled by the current layer should continue to be thrown after retaining the context;
- Exceptions that can be automatically repaired should be clearly classified as deterministic repairs;
- Non-deterministic exceptions must not be disguised as successes;
- Error handling logic must be clearly separated from main process responsibilities;
- Error reports to user output must be understandable,Error reports on log output must be troubleshootable;

## Log specifications
- Running status,critical branch,The reason for the failure must be reflected through logs or structured output;
- Logs must contain sufficient context,However, sensitive information must not be disclosed;
- Abuse prohibited `print` As a formal log scheme;
- Formal projects should be used uniformly `logging` Or project unified log component;
- Log levels must be semantically correct,For example `debug`,`info`,`warning`,`error`,`exception`;
- The high frequency path must not output noise logs;
- Error logs must help locate problems quickly;
- Log messages must be concise and clear,Avoid nonsense;
- Structured task output is preferred `JSON` Or can parse text stably;

## Input, output and interface
- Input and output formats must be stable;
- External interface field names must be fixed,Avoid implicit field drift;
- All external input must be verified for legality;
- External return content must be predictable,parsable,Compatible;
- Command line parameters must provide help descriptions;
- Command line parameter naming must be clear and consistent;
- Script exit codes must have clear semantics;
- Successful path return `0`,Failed paths must return a non-zero exit code;
- Important output must support automated consumption,Not intended for reading only by the naked human eye;
- Backwards incompatible changes must be documented,There is an explanation,Migration expected;

## File and path processing
- File path processing takes precedence `pathlib`;
- Path concatenation must not rely on hardcoded string concatenation;
- The existence of the path must be verified before reading and writing files.,permissions or createability;
- File writes must account for overwriting behavior,Atomicity and rollback on failure;
- involving deletion,move,The target behavior must be explicitly confirmed during operations such as overwriting;
- Temporary files must have a clear life cycle;
- Cross-platform path behavior must be considered ahead of time,It is forbidden to write according to the convention of a single system by default;

## Configuration management
- Configuration must be separated from code logic;
- Variable configuration must not be hard-coded in business code;
- Default configuration must be secure,keep,explainable;
- Configuration item naming must be stable;
- A clear error message must be given when configuration loading fails;
- Sensitive configurations must not be hard-coded and submitted to the warehouse;
- environment variables,Configuration file,The priority of command line parameters must be clear;
- When the configuration structure is complex, a unified reading entry must be provided;

## Testing and verification
- Script code must provide at least a minimum executable verification path;
- Critical logic must have minimum unit test coverage;
- Complex branches must cover the normal path,Boundary paths and failure paths;
- Test names must express scenarios and expectations;
- Tests must be stable,Repeatable,Do not rely on random external state;
- Testing must not contaminate the real environment;
- Tests that require external dependencies should be isolated or mock;
- return bug Corresponding tests should be supplemented;
- Critical path commands must support non-zero exit codes;
- Important functions must have at least one automated verification method;

## Concurrency and asynchronous
- Only use async or concurrency when there is a real benefit;
- Asynchronous function boundaries must be clear,Prohibit synchronization and asynchronous chaos interleaving;
- Concurrency logic must explicitly consider shared state safety;
- Not allowed in ununderstood threads,process,Concurrency at will under the premise of coroutine semantics;
- time out,Cancel,Try again,Resource release must be clearly designed;
- Concurrency failures must be observable,recyclable,Targetable;

## Performance requirements
- Prioritize accuracy and clarity,Further performance optimization;
- Performance optimization must be based on clear bottlenecks,instead of guessing;
- Repeated calculations in high-frequency paths,Repeat parsing,repeat `IO` must be avoided;
- Big data processing must control memory usage;
- Prefer streaming or segmented methods for batch processing;
- Cache must have clear boundaries,Failure strategies and consistency expectations;
- Do not sacrifice overall readability for small gains;

## security requirements
- Disallow hard-coded passwords,key,Tokens and sensitive credentials;
- log,abnormal,Sensitive information must not be revealed in debug output;
- External input must undergo legality verification and necessary cleaning;
- Command injection must be prevented when executing external commands;
- File operations must prevent risks such as path crossing;
- Deserialization,dynamic execution,High-risk capabilities such as template rendering must be used with caution;
- Any destructive operation must be explicitly controlled;
- The default policy must be more secure;

## Engineering maintainability
- Module responsibilities must be clear,Directory structure must be predictable;
- General capabilities should be accumulated and reused,Avoid scattered and repeated implementations;
- Code reviews must focus on correctness,boundary,compatibility,Readability and risk;
- Technical debt must be visible,Must not remain hidden in implementation details for long periods of time;
- Changes must control the scope of impact;
- Major changes must be implemented step by step first,Avoid introducing too much uncertainty at once;
- All key implementations should be as locationable as possible,Can be rolled back,auditable;

## Prohibited matters
- Key to disabling unhandled exceptions `IO` operate;
- Empty is prohibited `except`;
- prohibit `from xxx import *`;
- Disable the use of mutable objects as default parameters;
- Do not hardcode sensitive information in core logic;
- It is forbidden to accumulate duplicate logic through copy and paste.;
- Meaningless comments and expired comments are prohibited;
- Prohibit ambiguous naming;
- Disable returning unstable data structures;
- Disable debugging code,temporary hack,Useless code remains in the master branch for a long time;