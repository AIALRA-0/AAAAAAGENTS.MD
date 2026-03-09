---
last_updated: 2026-03-08-15-50
---

# JSON STANDARD

## Basic requirements
- all `JSON` The file must use `UTF-8` coding;
- all `JSON` Documents must be of legal standard `JSON`,Non-standard extended syntax may not be used;
- Comments are prohibited,because of standards `JSON` Annotations are not supported;
- Trailing commas are prohibited;
- Single quotes are prohibited,Strings must use double quotes;
- All key names must be strings;
- All structures must be guaranteed to be standard `JSON` The parser parses directly;
- Document content must be clear as a priority,Stablize,Maintainable,parsable;

## structural requirements
- Top-level structures must be fixed,and consistent with business semantics;
- The top-level structure of files of the same type must be unified,For example, unify into objects or unify into arrays;
- If there is no special reason,Top-level structures use objects first;
- All object structures must be hierarchically clear,Uncontrolled nesting is prohibited;
- The data hierarchy should be as flat as possible,Avoid deep nesting that affects readability and maintainability;
- Data with fixed semantics must use fixed fields,Do not drift at will;
- Data with the same semantics must maintain the same structure in different locations;
- There must be clear rules for the use of empty structures,For example, empty object `{}` or empty array `[]` The meaning of must be stable;

## Key name specification
- All key names must be semantically explicit,It is forbidden to use meaningless key names,For example `a`,`b`,`tmp`,`data1`;
- Key name styles in the same project must be consistent;
- If there is no special agreement,Recommended to use uniformly `snake_case` or `camelCase`,Do not mix;
- Only one name can be used for the same semantics,Synonymous fields are not allowed to coexist;
- It is prohibited to modify existing key names at will.;
- Key names must be stable,Avoid compatibility issues caused by naming changes;
- Boolean fields should be named to convey true and false semantics,For example `is_enabled`,`has_error`,`can_retry`;
- List field names should reflect collection semantics;
- time,state,type,High-frequency fields such as identifiers must be named uniformly;

## Value type requirements
- The value type of each field must be stable;
- The same field cannot be arbitrarily changed in type in different records;
- Numeric fields must clearly distinguish between integer and floating point semantics;
- Boolean fields must use standard boolean values `true` or `false`;
- NULL values ​​can only be used `null` Express;
- Empty strings are prohibited,`0`,`false`,Empty array replacement `null`,Unless the specification explicitly allows;
- Enumeration fields must limit the range of allowed values;
- The identification field must ensure uniqueness or a clear uniqueness range;
- The time field format must be consistent,It is forbidden to mix multiple time formats in the same file;

## Array requirements
- The elements in the array must be of the same type;
- Multiple unrelated structures must not be mixed in the same array;
- If the array element is an object,Then the object field set should be as consistent as possible;
- If array order has business meaning,must be stable;
- If the array order has no business meaning,should be made clear in the specification;
- Empty arrays must have explicit semantics,Not to be abused;
- Large arrays should be considered splittable,Paging or streaming needs;
- It is forbidden to force irrelevant data into the same array;

## Object requirements
- Object fields must have clear responsibilities;
- Objects must not be stuffed with fields that have nothing to do with their semantics;
- Fixed structure objects must keep the collection of fields stable;
- Whether a field is required must be explicitly constrained;
- Required fields must not be missing;
- Whether optional fields allow defaults,Is it allowed? `null` must be clearly defined;
- Nested objects within objects must have clear semantic boundaries;
- Do not use superwide objects to carry too much extraneous information;

## readability requirements
- Document layout must be consistent;
- Recommended to use uniformly `2` or `4` space indent,No mixing is allowed within the project;
- The order of fields in the same type of files should be kept as stable as possible;
- High priority fields should be placed first;
- The order of fields in the same structure object should be as consistent as possible;
- Long documents should be kept logically grouped clearly;
- Source file readability must not be sacrificed for compression size,Unless the file is explicitly a build artifact;
- When the structure is complex,Should be accompanied by independent specifications or schema illustrate;

## Compatibility requirements
- Fields already in use must be as backwards compatible as possible;
- New fields should be expanded optionally first;
- Compatibility impact must be assessed before field deletion;
- Modifying field semantics must be considered a high-risk change;
- Existing fields must not be renamed without a migration plan;
- Enum value extensions must take into account legacy consumer behavior;
- Input and output formats must be stable,Avoid implicit field drift;
- Backwards incompatible changes must be clearly documented and migrated with instructions;

## Schema Verification
- important `JSON` Documents must have clear structural constraints;
- Recommended for core structures `JSON Schema` or equivalent verification rules;
- All automation dependent fields must be stably validable;
- Required fields,Field type,enumeration value,Default behavior must be definable;
- Validation rules must be synchronized with actual data;
- When verification fails, a clear statement must be given.,Locatable error messages;
- Must be updated simultaneously after structural changes schema or corresponding documents;
- The verification requirements for generated class files and handwritten class files should be consistent;

## Default value and empty value
- Default value policies must be unified;
- If the field can be defaulted,then the default semantics must be specified;
- If the field allows `null`,it must be clear `null` The business meaning of;
- Simultaneous use prohibited"Field missing"and"The fields are `null`"express the same meaning,Unless the specification clearly distinguishes;
- Default should be select safe,Predictable,interpretable value;
- Boolean fields must avoid tristate problems;
- Empty strings should only be used in scenarios where empty text is explicitly required;
- Empty arrays and empty objects must retain their structural semantics,It is not allowed to substitute other null value expressions at will.;

## Time and logo
- Time fields must be in a uniform format;
- If there are no special requirements,Recommended `ISO 8601` Format;
- Time fields must specify time zone semantics;
- Do not mix local time and UTC time without explanation;
- Identity field naming must be consistent,For example, use unified `id`,`name`,`type`,`status`;
- The identity value must remain stable,It is prohibited to use display copy as a unique identifier;
- If there is a primary key,foreign key,Reference relationship,References must be traceable;
- Status fields must be limited to a predefined collection;

## security requirements
- prohibited from `JSON` Store password in clear text in file,private key,key,Sensitive information such as tokens;
- Submissions containing production environment credentials are prohibited `JSON` document;
- log,Export,generated by debugging `JSON` Sensitive fields must not be disclosed;
- generated by external input `JSON` Must pass legality check;
- The deserialized fields must be verified by the business layer before use.;
- Data from untrusted sources must not be written directly to the core configuration;
- Any sensitive fields must be desensitized,Quarantine or controlled policy;
- Sensitive fields in test data must use fake values;

## Profile requirements
- for configuration purposes `JSON` Documents must be kept concise;
- Configuration item naming must be clear,Stablize,predictable;
- Variable configuration must not be mixed with runtime generated data;
- Default values ​​in configuration files must be safe;
- Configuration items give priority to reflecting business meanings,rather than underlying implementation details;
- Dependencies between configuration items must be clear;
- High-risk configurations must have explicit switches or additional constraints;
- Changes to configuration fields must be updated simultaneously on the user side;

## Data file requirements
- For data storage purposes `JSON` Files must have a consistent structure;
- The set of object fields in batch records should be as unified as possible;
- Data files must not be mixed with irrelevant meta-information,Unless the specification explicitly requires;
- Statistics,Cache class,Snapshot class files must be semantically distinct;
- Generated data and manual maintenance data should be separated as much as possible;
- Splitting strategies must be considered for large volumes of data;
- Data update strategy must be clear,For example, full coverage,incremental append,key replacement;
- There should be a clear strategy for deleting data,Key records must not be lost silently;

## Logging and output requirements
- For automated consumption `JSON` The output must be field stable;
- Log type `JSON` Must contain sufficient context to support troubleshooting;
- Output fields should avoid being mixed with display-only human text;
- critical state,error message,Contextual identification should be expressed in a structured way;
- Error output must be localizable;
- Important output preferentially uses parsable objects.,Instead of concatenating strings;
- Field extensions must consider existing consumer compatibility;
- There should be clear boundaries between different output types,Avoid mixed semantics;

## Generation and maintenance requirements
- automatically generated `JSON` Documentation should be clearly distinguished from manual maintenance documentation;
- Automatically generated files should not be modified manually,Must be clearly identified;
- Manual maintenance files must keep the format stable,reduce meaninglessness diff;
- Field order,indentation,Line break style should be as fixed as possible;
- The scope of impact must be controlled when making changes;
- Core structure changes must update the consumer side simultaneously,Verification rules and documentation;
- Key field semantics must not be changed silently;
- Files with high historical compatibility requirements must have a change audit mechanism;

## Performance and volume requirements
- Not in a single `JSON` Unlimited accumulation of large volumes of data in files;
- High-frequency reading and writing of files must consider the cost of parsing;
- Large files should be evaluated for splitting,index,Pagination or binary alternative;
- Do not embed large blocks of irrelevant data in configuration class files;
- The same data must not be repeated meaninglessly and redundantly;
- Volume-sensitive scenes can be compressed,But the source file specification should still remain maintainable;
- Structural design should take into account transmission costs and clear expression;
- Performance optimization must not undermine structural stability;

## Testing and verification requirements
- important `JSON` The file must have a minimum verification path;
- Should at least cover legal samples,Illegal sample,Boundary sample;
- Automated verification should be provided for critical configuration and core data;
- When verification fails, it should be able to locate the field level;
- Old data compatibility must be verified after changes;
- rely `JSON` The core logic must have regression testing;
- Sample data should be as close to the real usage scenario as possible;
- Test data must not pollute formal data structures;

## Prohibited matters
- Non-standard use is prohibited `JSON` grammar;
- Comments are prohibited;
- Trailing commas are prohibited;
- Mixing of multiple key name styles is prohibited;
- Prevent semantic drift of the same field in different places;
- Substituting display copy for structured fields is prohibited;
- Prohibit storing credentials in clear text in sensitive scenarios;
- No documentation is prohibited,Arbitrarily extend core structures without validation;
- Forbidden to be missing,`null`,empty string,Empty arrays are lumped together;
- Disallow cramming multiple unsplit semantics into a single field;