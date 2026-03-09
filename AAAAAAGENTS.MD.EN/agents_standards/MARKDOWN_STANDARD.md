---
last_updated: 2026-03-08-15-50
---

# MARKDOWN STANDARD

## Basic requirements
- All documents must use `UTF-8` coding;
- The use of Chinese periods in the entire text is prohibited `.` and English period `.`,Use semicolons at the end of all sentences `;`;
- Document content must be concise and clear,Banning the use of generic,Vague,colloquial expression;
- Document content must remain readable,Maintainable,parsable;
- Tone in the same document,the term,Field styles must be consistent;

## Title requirements
- All documentation must use standards Markdown Title syntax;
- Only one first-level heading is allowed per document `#`;
- Second level title names must be short,clear,Stablize;
- The title level must not be skipped;

## List requirements
- All text content is used uniformly `-` list expression;
- Use all indents uniformly `-` List indentation;
- No mixing `*`,`+`,Ordered list or other indentation;
- The indent widths of sibling lists must be consistent;
- Subordinate lists must be indented only one level more than superior lists.;
- Long content must be split into multiple short list items,Disable stacking of growing paragraphs;

## Marking requirements
- All code blocks must be marked with language type,For example `markdown`,`yaml`,`json`,`bash`,`python`,`text`;
- All code blocks,file path,variable name,Field name,Order,Identifiers must be wrapped in backticks;
- Configuration keys in all examples,status value,Parameter name,Directory names must be wrapped in backticks;
- All path expressions must maintain a consistent format;
- All variable naming must be stable and consistent,It is prohibited to repeatedly change the name of the same concept;
- All field names must be fixed,It is forbidden to change the name at will;

## Formula requirements
- all LaTeX Inline formulas must be used `$...$`;
- all LaTeX Block level formulas must use `$$...$$`;
- The use of non-standard formula wrapping methods is prohibited;
- The naming of variables in the formula must be consistent with the text;

## Content requirements
- Content that requires machine parsing must be in a format that can be stably parsed;
- Structured content must ensure that key names are stable,Clear hierarchy,Consistent format;
- Required fields cannot be left blank;
- Whether non-required fields are allowed to be empty,must be clearly defined in advance;
- All examples must be minimized,Keep only necessary content;
- Wrong examples and correct examples must be clearly distinguished;
- It is forbidden to include complex content in the example that is not relevant to the current rules.;

## Consistency requirements
- When Chinese and English are mixed,Terminology must be consistent;
- The same concept can only use one name in the same document;
- Rule expressions must be used first"must""prohibit""Not allowed""only allowed"Wait for clear wording;
- Prohibited use"almost""perhaps""Will make up for it later"Such uncertain expressions;
- It is prohibited to leave meaningless placeholder content,For example"To be added""None yet""Talk about it later";
- Content that automation relies on must not rely solely on visual layout judgments;

## Prohibited matters
- Periods are prohibited;
- The use of third-level headings and below is prohibited;
- Numbered titles are prohibited;
- It is forbidden to write code blocks directly without backticks.,path,variable,Field,command or identifier;
- It is prohibited to mix multiple sets of inconsistent formatting styles.;
- It is forbidden to use free-form writing that will affect the stability of parsing.;
- Decorative typography that is not relevant to the content is prohibited;
- Forbidden to leave semantics incomplete,Content with incomplete structure or incomplete rules;