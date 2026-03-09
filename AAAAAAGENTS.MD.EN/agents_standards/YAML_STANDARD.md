---
last_updated: 2026-03-08-15-50
---

# YAML STANDARD

## Basic requirements
- all `YAML` The file must use `UTF-8` coding;
- all `YAML` The file must use `.yaml` or `.yml` unified suffix,and be consistent within the project;
- in the same project `YAML` style,Field naming,Indentation rules,Boolean writing,Null values ​​must be written consistently;
- all `YAML` Content must be readable as a priority,Maintainability and parsability;
- `YAML` Must be able to be stably parsed by mainstream parsers,Reliance on ambiguous behavior is prohibited;
- The configuration structure must be clear,Stablize,Predictable;
- It is forbidden to write something difficult to read just to save trouble.,Difficult to maintain,Disaster diff format;

## Format requirements
- All indents must use spaces.,Prohibited use `Tab`;
- Indent width must be uniform within the project,Commonly used `2` or `4` spaces;
- Do not mix different indent widths in the same file;
- Keys and values ​​must be separated by a space,For example `key: value`;
- Spaces must remain after the colon,It is forbidden to write `key:value`;
- Use list items uniformly `-` express,and stay aligned with content at the same level;
- Sibling keys must be left aligned;
- The use of blank lines must be restrained,Only used to separate logical blocks;
- No extra spaces should be left at the end of the line;
- A newline must be left at the end of the file;

## Key name specification
- Key names must be semantically clear,Use of meaningless names is prohibited,For example `data1`,`tmp`,`foo`,`bar`;
- The same concept must use the same key name in the same project,Prohibit mixing of synonymous fields;
- Key name styles must be consistent,Usually used uniformly `snake_case` Or the established style of the project;
- It is prohibited to arbitrarily change key names that have been used externally.;
- Key names must be stable,Avoid frequent drift;
- The key name must reflect the business meaning,rather than implementation details;
- Do not mix key names with inconsistent styles at the same level;

## How to write value
- string,number,Boolean value,The expression of null values ​​must be consistent;
- Boolean values ​​are used uniformly `true` and `false` lowercase form;
- Null values ​​must be written uniformly,Commonly used `null` or leave blank,But one must be fixed within the project;
- Numeric values ​​should maintain true numeric semantics,Avoid writing numbers as strings;
- Leading zeros need to be preserved,When special formatting or avoiding ambiguity,Strings must be used explicitly;
- date,version number,Identifiers and other values ​​that are easily misparsed,It is recommended to use quotation marks;
- Do not rely on the parser's guessing behavior for implicit types;
- The type of the value must match the field definition,The same field must not change types repeatedly in different entries;

## Quotation mark specification
- Prefer simple unquoted scalars by default;
- When the value contains special characters,colon,Leading zeros,white space boundary,boolean ambiguity,Date ambiguity or template symbol,Quotation marks are required;
- The style of string quotation marks in the same project should be as uniform as possible;
- Use single quotes first when you need to avoid escaping;
- Use double quotes when you need to express escape characters;
- All values ​​must not be mechanically quoted;
- Do not omit quotation marks when they are required resulting in semantic ambiguity;

## structural design
- `YAML` Structure must be clearly layered,Avoid meaningless deep nesting;
- Field granularity at the same level should be as consistent as possible;
- Fixed structure data should maintain a stable order;
- The order of fields should be as consistent as possible with reading and usage habits.;
- The top-level structure must be concise and clear,Do not accumulate too many irrelevant fields;
- Complex configurations must be split into multiple logical blocks,rather than cramming in a very large object;
- Repeated structures should be as abstract and consistent as possible,Avoid having different structures for similar items;
- Required fields must always be present;
- Whether optional fields are allowed to be empty must be explicitly stated by the specification;
- Structure must serve readability and parsability,Rather than just for the convenience of writing;

## List specification
- Collections of similar objects are preferably expressed in lists.;
- The structure of each item in the list must be as consistent as possible;
- The order of fields in list items should be consistent;
- Required fields in the list must not be missing;
- An empty list must be explicitly written as `[]` Or a unified writing method for the project;
- Single-item lists should also maintain list semantics,May not be degenerated into a single object at will;
- When list items are too complex, you must consider extracting them into a clearer hierarchical structure.;
- Do not mix entries of different semantic types in the same list;

## Annotation specifications
- Comments must explain why,constraint,Boundaries and special behaviors,Instead of reciting the surface meaning of the field;
- Simple and intuitive fields must not add uninformative comments;
- Annotations must be kept in sync with configuration content;
- Expired comments must be deleted or updated promptly;
- Comments should be concise and clear,Long descriptions are prohibited;
- key default,Risk items,Compatibility requirements,Restrictions should be explained in comments;
- Emotional use is prohibited,Colloquial or personalized comments;
- Temporary annotations must not remain in the official configuration for long periods of time;
- Areas that require strict machine parsing,It is necessary to confirm that the annotation does not affect the parsing process;

## Compatibility requirements
- all `YAML` Files must be compatible with mainstream `YAML 1.2` parse expectations;
- It is prohibited to rely on non-generic features of a specific parser as core capabilities;
- Do not use ambiguous writing methods that may cause cross-language parsing differences.;
- Key configuration must consider parsing consistency across different language implementations;
- Exposed to the outside world or consumed across systems `YAML`,Priority must be given to conservative writing;
- Content that needs to be read stably by the machine,should be as close as possible `JSON-compatible YAML`;
- Do not abuse advanced syntax in critical configurations to reduce portability;

## Parsability requirements
- Requires machine analysis `YAML` It is necessary to ensure that the key name is stable,Fixed level,Well typed;
- Automation dependent fields must not be inferred solely through visual typography;
- Key fields must be clear,only,stable semantics;
- The meanings of fields with the same name in different contexts must not conflict;
- Objects of the same type must share a unified structure;
- Do not mix free-form text in structured areas;
- Do not use writing methods that make the parsing logic rely on vague conventions.;
- Structures that require long-term evolution must consider backward compatibility;

## Reuse and anchor points
- `YAML` anchor point,Alias,Merge keys should only be used when absolutely necessary;
- Use advanced reuse syntax only if it can be stably understood and maintained by the project team;
- Anchors should be used with caution in critical configurations,Avoid increased reading and debugging costs;
- Do not introduce obscure anchor structures just to reduce duplication in a few lines;
- If using anchors and aliases,Naming must be clear;
- Do not rely on anchors making the final semantics difficult to track;
- When cross-tool compatibility is required,Prioritize the use of advanced features with weak compatibility;

## File organization
- Large configurations should be split logically,Instead of maintaining a very large single file for a long time;
- Multiple after splitting `YAML` Files must have clear boundaries and loading order;
- File naming must be clear,Stablize,Predictable;
- Configuration files of the same type should use a unified naming convention;
- template file,Sample file,Formal configuration files must clearly distinguish;
- The configuration coverage relationship must be clear,For example, basic configuration,Environment configuration,partial coverage;
- Do not allow implicit,Difficult to trace coverage chain;

## Environment and configuration management
- Variable environment configuration must not be hard-coded in business logic;
- Default configuration must be secure,keep,explainable;
- Configuration differences between environments must be expressed explicitly;
- develop,test,Production and other environment configurations should be clearly separated;
- Environment-specific fields must be explicitly stated;
- Configuration override rules must be predictable;
- Sensitive configuration must not be written directly to publicly commitable files;
- Sensitive values ​​that need to be injected should be provided in a safe way,Instead of plain text hardcoding;

## security requirements
- prohibited from `YAML` Medium hardcoded password,key,token,Sensitive information such as private keys;
- If you need to display sensitive fields in the sample configuration,Placeholder values ​​must be used;
- log,debug,The export process must not reveal sensitive configurations;
- High-risk configuration items must be clearly annotated;
- The default value must be safe;
- delete,cover,remote execution,Destructive configurations such as privilege escalation must be explicitly controlled;
- Shared externally `YAML` Sensitive information must be checked first;
- Temporary credentials must not be mistakenly submitted into the official configuration;

## Changes and Compatibility
- Fields that have been put into use cannot be deleted or renamed at will.;
- Backward-incompatible structural changes must be clearly documented;
- Changes must control the scope of impact;
- When adding new fields, try not to destroy the old parsing logic.;
- Abandoned fields should have a transition period,rather than immediately and silently removing;
- Default value changes must be clearly documented;
- The semantics of the same configuration item must not drift without explanation.;
- All major structural adjustments should prioritize ensuring that migration is controllable;

## Verification requirements
- all `YAML` Files must pass syntax check before submission;
- Key configuration files should add structure check or `schema` check;
- Required fields,Field type,Allowed value ranges should be automatically verified;
- Enumeration values ​​should be limited to explicit collections whenever possible;
- Error messages must help quickly locate the problem;
- Configuration validation must cover syntax,Structure and key semantics;
- Automatic repair must be limited to deterministic format repair;
- Non-deterministic configuration issues must be explicitly corrected by humans;

## readability requirements
- The division of configuration blocks must conform to reading habits;
- Highly relevant fields should be placed as adjacent as possible;
- The order of fields of similar objects must be consistent;
- Do not sacrifice readability for the sake of compressed lines;
- Long texts should consider using appropriate multi-line writing;
- Configuration files should be as human-readable as possible,Differences are easy to see,Problems are easy to find;
- Complex values ​​must be accompanied by sufficient context;
- Areas that are frequently modified should be structurally stable as much as possible,reduce meaninglessness diff;

## multiline text
- Multi-line text must be written in an appropriate way based on semantics;
- Use reserved block scalars when you need to preserve line breaks;
- Use folding block scalar when folding and wrapping are required;
- Multiline text must be indented correctly;
- Whitespace and trailing newline behavior in multiline text must be expected;
- Do not mix multiline text with indentation that breaks the parsing hierarchy;
- Multiple lines of content that need to be accurately consumed by the program must clearly state the format requirements;

## Prohibited matters
- Prohibited use `Tab` indentation;
- Do not mix different indent widths;
- Disable confusing field naming;
- Disable drift of the same field type;
- Disallow reliance on implicit type guessing;
- Disallow the abuse of anchors in critical configurations,Alias,merge key;
- Disallow meaningless comments in formal configurations,Temporary comments,Debugging remnants;
- Hard coding of sensitive information is prohibited;
- It is forbidden to use writing methods that cannot work stably across parsers.;
- Submissions that have not undergone basic syntax verification are prohibited. `YAML` document;