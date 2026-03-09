---
last_updated: 2026-03-08-22-02
---

# TEXT STANDARD

## Basic requirements
- all `TXT` The file must use `UTF-8` coding
- all `TXT` Document content must be directly readable,No reliance on special editors or proprietary formats
- all `TXT` Documents must be clear as a priority,Stablize,Maintainable,auditable
- in the same project `TXT` Document writing style,Field naming,separation method,Time format must be consistent
- `TXT` File is for plain text description,Log output,inventory record,Brief configuration,Debugging results,Scenarios such as snapshot information
- Not suitable for complex hierarchical structures,Strongly structured data or content with rich text formatting,should not be used forcefully `TXT` Express

## File naming
- File names must be concise and clear,Can directly reflect the use
- File names should avoid unsemantic naming,For example `tmp.txt`,`test.txt`,`new.txt`
- Similar text files must be named in a consistent style
- It is recommended that the file name use stable English lowercase letters with underscores or a unified naming rule for the project.
- File names containing time dimensions should use a unified time format,For example `YYYY-MM-DD` or `YYYY-MM-DD-HH-MM`
- Temporary documents and official documents must be clearly distinguishable in their naming

## Content organization
- each `TXT` Documents must have a clear beginning,Do not directly stack scattered content
- Content should be organized in a fixed order,Avoid similar information being placed out of sequence
- in the same document,Information of the same type should be placed together
- Long content must pass through blank lines,Separation by fixed prefix or stable segmentation
- Do not mix different organizational methods in the same document
- Text templates of the same type should try to keep the same field order and layout.

## readability requirements
- Text expression must be concise,clear,direct
- Blur is prohibited,colloquial,Emotional or uninformative expressions
- Long sentences should be broken into short sentences or separate lines as much as possible
- The information density at the same level should be as consistent as possible
- Text should be designed to be quickly scannable and understandable by humans.
- Do not squeeze multiple independent pieces of information into one line
- Important information must have stable identification,Easy to search and locate

## structural constraints
- like `TXT` Files carry semi-structured content,Must use fixed format
- Entries of the same type must use the exact same field order
- Field names must be stable,Synonymous substitution or frequent name changes are prohibited
- There must be a clear separation between fields
- There must be clear boundaries between items
- Required fields must not be missing
- Whether non-required fields are allowed to be empty,must be explicitly stated by the specification
- Need to be consumed by the program `TXT` The file must be in a format that can be stably parsed
- Do not mix free narrative content into structured areas

## Row format requirements
- Each line should carry only one clear semantic unit
- Beginning of line indent,prefix symbol,Separators must be used uniformly
- Blank lines should only be used to separate paragraphs,No random insertion is allowed
- No meaningless spaces should be left at the end of the line
- Multiple lines of records must remain visually and logically aligned
- The newline style must be consistent in the same file
- Do not mix different list or delimiter styles

## Separation and identification
- Delimiters must be uniform and predictable
- If used `:`,`=`,`|`,`\t` equal separator,Must be consistent throughout the document
- The rules for spaces before and after delimiters must be consistent
- identifier,Field name prefix,Status prefix must be fixed
- It is recommended to use searchable keyword prefixes for important records,For example `status:`,`error:`,`path:`
- It is prohibited to use multiple random separation methods at the same time in the same document.

## time and status
- All time expressions must be in a consistent format
- Recommended `YYYY-MM-DD HH:MM:SS` Or the time format specified by the project
- Status values ​​within the same project must remain a fixed set
- State naming must be clear,enumerable,Comparable
- Do not use multiple synonyms for the same state
- involves order,The text content of the stage or life cycle,It is necessary to ensure that the state flow logic is consistent

## Paths and commands
- All path expressions must be in the same format
- Paths should try to use relative paths or fixed representations specified by the project.
- All commands must be written completely and can be copied and executed
- There must be a clear boundary between commands and ordinary description text
- The order of command parameters must be stable
- Do not mix meaningless descriptive characters into command text
- path,Order,It is recommended to use a uniform highlighting method or a fixed prefix for identifiers in the text.

## Log text
- Log class `TXT` File must contain time,level,event,Core information such as context
- Similar log records must use a fixed format
- Log output must be fully searchable,Filtering and subsequent archiving
- Error logs must contain locatable context
- success,fail,warn,Debug information must be distinguishable
- High frequency logs must not produce excessive noise
- Passwords must not be revealed in the logs,key,token,Personal sensitive data and other information
- Exception logs must try to retain enough context,But avoid being so lengthy that it affects the efficiency of the investigation.

## List text
- List class `TXT` Documents must ensure one thing and one meaning
- Each inventory record should be uniquely identifiable
- List item sorting must be fixed,For example by name,path,Time or priority sorting
- Lists should not be mixed with narrative content that is not relevant to the goals of the list
- Completed,Not completed,Deleted,Statuses such as skipped must have a unified identification method
- Checklist text must facilitate difference comparison and manual review

## Output class text
- Programmatically generated output classes `TXT` Files must remain in a stable format
- Try to generate consistent output under the same input conditions.
- The output content should give priority to ensure certainty,Reduce meaningless fluctuations
- The order of fields in the output must be fixed
- the value in the output,path,state,Statistical items must be clearly labeled
- For text output for subsequent program processing,Parsability must first be guaranteed,Consider display again

## Notes and explanations
- Descriptive content in plain text must be concise and meaningful
- If annotation semantics are required,A uniformly agreed upon annotation prefix must be used
- Annotations must not be confused with formal data
- Comments should explain why,limit,background or special circumstances,rather than repeating surface content
- Expired instructions must be deleted or updated promptly
- Not allowed to use"Talk about it later""Pending""First like this"Description of long-term suspension

## Compatibility requirements
- Text content should be compatible with common operating systems and common editors
- Do not rely on invisible characters to carry key semantics
- No reliance on specific fonts,Align Width or Renderer Effect Expression Structure
- For text files that need to be transferred across platforms,Platform-specific special writing must be avoided
- For text files that require long-term archiving,Content must be understandable out of context

## Maintenance requirements
- Once a document forms a public agreement,Field,order,The format cannot be changed at will
- Format changes must have clear reasons and compatibility policies
- Historical text if used for auditing,Do not overwrite or rewrite at will
- Automatically generated files and manually maintained files must be clearly distinguished
- Text templates should be as fixed as possible,Reduce reinvention of the wheel
- For frequently generated text,Priority should be given to designing to facilitate `diff` and version management forms

## security requirements
- prohibited from `TXT` Record the password in clear text in the file,private key,token,Sensitive credentials
- Do not disclose personally identifiable information in logs or output,Key information or internal sensitive paths
- Text files to be shared,Content desensitization must be confirmed in advance
- If sensitive information must exist,There should be clear access controls and usage instructions
- Sensitive content in temporary debug output must not be retained long-term

## Prohibited matters
- Unstable use is prohibited,Unpredictable free form
- It is prohibited to mix multiple sets of field names or separation rules in the same file.
- No untitled,no context,Stack content without structure
- Disguising complex structured data as loose text is prohibited
- The use of generic names is prohibited,Fuzzy status and meaningless placeholder content
- Disallow debug noise in official text,Obsolete content and expiration instructions
- It is prohibited to randomly insert natural language paragraphs into text that requires machine processing.
- It is forbidden to leave isolated lines whose semantic belonging cannot be determined.
- Prohibition of expressing core semantics through visual alignment rather than explicit identification
