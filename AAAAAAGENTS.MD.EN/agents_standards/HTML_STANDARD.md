---
last_updated: 2026-03-08-22-02
---

# HTML STANDARD

## Basic requirements
- all `HTML` The file must use `UTF-8` coding;
- All pages must declare a standard document type `<!DOCTYPE html>`;
- All page root nodes must use `<html>`,and explicitly declare `lang` property;
- All documents must be clearly structured,Clear semantics,Maintainable,Expandable;
- Label styles in the same project,Attribute order,indent style,Naming style must be consistent;
- It is forbidden to abuse non-semantic tags for visual effects;
- The page structure must prioritize ensuring correct semantics,Consider style performance again;

## Document structure
- All pages must contain `<head>` and `<body>`;
- `<head>` must contain at least `meta charset`,`viewport`,`title`;
- `<title>` Content must accurately express the current page topic;
- `<body>` The main content must have a clear structure;
- The main content of the page should be placed in a semantic container first,For example `<main>`;
- global navigation,Header,footer,Semantic tags should be used first in side areas,For example `<header>`,`<nav>`,`<footer>`,`<aside>`;
- Pages must not contain meaningless deeply nested structures;
- Block division must serve content and semantics,Do not add redundant containers just for the sake of leveling up;
- Document structure must remain stable,Convenient for styling,Script and test positioning;

## Semantic requirements
- Content areas must use semantic tags first,instead of using all `<div>`;
- Titles must use standard title tags `<h1>` arrive `<h6>`;
- There should be only one main title on the page as much as possible `<h1>`;
- Title hierarchy must be in logical order,Not allowed to skip levels;
- List content must use `<ul>`,`<ol>`,`<li>`;
- Paragraph content must use `<p>`;
- Emphasize that content must be chosen based on semantics `<strong>` or `<em>`;
- Quotes must be `<blockquote>` or `<q>`;
- time,address,code,Tables and other content should use corresponding semantic tags;
- It is forbidden to use pure style tags to replace semantic expressions;

## Accessibility requirements
- All interactive elements must be keyboard accessible;
- All form controls must have associated `<label>`;
- Images must provide meaningful `alt` text,Purely decorative images should use empty `alt`;
- All buttons must be used `<button>` or have equivalent semantics,Don't use inaccessible elements to disguise buttons;
- Link must use `<a>`,and provide clear and understandable text;
- Prohibited use"Click here""More"This type of link text loses its meaning when taken out of context;
- There must be sufficient contrast between the text and the background;
- Reliance on color as the sole means of conveying information must be avoided;
- Form error messages must be perceptible and understandable;
- dynamic area,Pop-up window,menu,Complex components such as tabs must have clear accessibility state and focus management;
- Page structure must be easy for screen readers to understand;
- all `iframe` Must provide understandable `title`;

## Label and attribute requirements
- Labels must be closed correctly;
- Attribute values ​​must be wrapped in double quotes;
- Property naming and usage must be consistent;
- Boolean attributes must use standard writing;
- Custom attributes must be used `data-*` prefix;
- Deprecated tags and deprecated attributes are prohibited;
- Adding meaningless or unused attributes is prohibited;
- The same attribute order should be maintained for similar elements;
- Do not stack unmaintainable long attribute strings in tags;
- Structural properties,Behavioral attributes,Style attributes should keep their responsibilities clear;

## Indentation and formatting
- Indentation style must be consistent within the project,For example, use unified `2` or `4` spaces;
- Labels at the same level must be aligned;
- Long attribute lists should be arranged in new lines,remain readable;
- White space and line breaks should serve readability,No meaningless formatting is allowed;
- Comment,property,Label layout must be as stable as possible,Reduce meaningless differences;
- Template files and purely static pages should maintain a unified format specification;
- Do not mix different formatting styles;

## Annotation specifications
- Comments must state structural intent,boundary,Limitations or unintuitive design reasons;
- It is forbidden to add nonsense comments that duplicate the surface meaning of the code.;
- Temporary instructions,Compatibility processing,Special dependencies,Accessibility exceptions should be clearly annotated;
- Expired comments must be deleted or updated promptly;
- It is forbidden to retain large comment blocks that have no maintenance value.;
- Comments must be concise and clear,Don’t be emotional or verbal;
- Block-level comments should prioritize describing regional responsibilities,Rather than describing specific style effects;

## style border
- `HTML` Responsible for structure and semantics,Do not mix a lot of presentation logic into the structure;
- Abuse of inline styles is prohibited `style`;
- Style class names must be semantically clear,Reusable,Maintainable;
- Structure class name,Status class name,Behavior hook class names must have clear responsibilities;
- It is prohibited to write style implementation details directly into structure naming.,Unless the project specifications specifically allow;
- theme,state,size,Layout and other changes should have a unified naming strategy;
- Page structure must not rely on fragile tag hierarchies to implement core styling logic;

## script boundaries
- `HTML` Complex script logic must not be inlined in;
- Abuse of inline event attributes is prohibited,For example `onclick`,`onchange`,`onload`;
- Behavior binding should be managed uniformly by script files first;
- Nodes that need to be recognized by scripts should use stable hooks,For example `id`,`data-*` or agreed class name;
- Structures must not be strongly coupled to specific scripts;
- The data entry that rendering depends on must be clear and clear;
- Dynamic content insertion must consider security and accessibility;

## Form specifications
- All form fields must be clearly labeled;
- Required fields,Optional,default value,Format requirements must be clearly expressed;
- Form grouping should use a reasonable structure,For example `<fieldset>` and `<legend>`;
- Input control type must match data semantics,For example, use email `type="email"`;
- Form validation must take into account both browser capabilities and business rules;
- Error messages must clearly indicate the problem and how to fix it;
- Placeholder text cannot replace labels;
- Submit buttons must have clear semantics;
- Form state changes must be perceptible;
- Sensitive input must be considered for autofill,Hiding and security strategies;

## Media and Resources
- picture,Audio,Resources such as videos must be semantically correctly embedded;
- Images must be of reasonable size or have a stable layout strategy,Avoid page jitter;
- Responsive images should use appropriate solutions as needed;
- Video and audio content must consider accessibility,such as subtitles or alternate descriptions;
- References to external resources must clearly identify their source and purpose;
- Resource paths must be stable,clear,Maintainable;
- Unused or duplicate resources must not be loaded;
- Third-party embedded content must have clear boundaries and risks;

## Table specification
- Only real tabular data can be used `<table>`;
- It is forbidden to use tables for page layout;
- Tables must contain clear headers;
- should be used when necessary `<caption>` Explain the purpose of the form;
- When the row-column relationship is complex, appropriate semantic tags must be added;
- Form content must be understandable on narrow screens and assistive technologies;
- Tables must not host interactive layouts that do not fit the semantics of the table;

## Links and Navigation
- Links must have clear destination semantics;
- Navigation areas should have a clear structure and identifiable boundaries;
- The current page or current item state must be identifiable;
- External link behavior must comply with the project's unified policy;
- New window opening behavior must be used with caution,and provide clear reminders when necessary;
- Anchor links must ensure that the target exists and targeting is available;
- bread crumbs,Pagination,Navigation components such as directories must have clear semantics,Consistently available;

## Performance requirements
- The document structure must be as concise as possible,Avoid meaningless node expansion;
- Key content above the fold must be available first;
- Resource references must avoid blocking the critical rendering path;
- picture,font,script,The performance impact must be considered when loading resources such as styles;
- Non-critical resources that can be loaded lazily should be loaded on demand;
- It is forbidden to introduce unused large front-end dependencies;
- Repeated template structures should be abstracted and reused first;
- Page size and number of nodes should be controlled within a reasonable range;

## security requirements
- All dynamically inserted content must prevent `XSS` risk;
- Disable trusting external input directly and writing to the page;
- external links,Embed content,All form inputs must consider security boundaries;
- Sensitive information must not appear directly in the page source code;
- Internal identifiers that should not be exposed to the public must not be exposed on the front end,key,Token or debug information;
- Source credibility must be evaluated when using third-party scripts and resources;
- Areas involving user input echo must be escaped or equivalently safe.;
- Security-related attributes must be set appropriately according to the scenario;

## SEO and meta information
- Page title must be accurate,concise,distinguishable;
- Pages should provide necessary descriptive meta-information;
- Important pages should ensure that the main content is clear and understandable to both search engines and users.;
- Title level,link text,Image alt text must contribute to content comprehension;
- Duplicate content pages should handle canonicalization issues per project policy;
- Do not use deceptive titles,Keyword stuffing or hidden content;
- The structured information of public pages must be true,Stablize,Maintainable;

## Internationalization and localization
- Page language must pass `lang` clear statement;
- Text content must not be hard-coded in locations that are difficult to maintain;
- time,number,currency,Directional content must consider localization;
- Multilingual pages must ensure consistent semantics and structure;
- Language switching logic must not be hard-coded at the structural level;
- Copy length changes must not disrupt the underlying structure;

## Testing and maintainability
- The structure must facilitate automated test positioning;
- The test positioning hook must be stable,Do not rely on fragile layers;
- Frequently used areas should have clear boundaries of responsibilities;
- Public structure consistency must be maintained when templates are reused;
- Styles must be evaluated when modifying a structure,script,test,accessibility and SEO influence;
- Large-scale page structure adjustments should be implemented step by step as a priority;
- Historical compatibility constraints must be clearly stated in comments or specifications;
- Page code must be easy to review,Positioning and rollback;

## Prohibited matters
- Forbidden to lack `<!DOCTYPE html>`;
- Forbidden to lack `lang`,`charset`,`viewport`,`title` Basic statement;
- Abuse prohibited `<div>` and `<span>` alternative semantic tags;
- It is forbidden to use tables for page layout;
- Disallow the use of inline event attributes to host core interactions;
- Extensive use of inline styles is prohibited;
- Deprecated tags and deprecated attributes are prohibited;
- No semantics are allowed,no accessibility,Structural stacking with no maintenance value;
- Prohibited pictures lacking reasonable `alt`;
- Suppress form control missing label;
- Do not treat placeholder text as an official label;
- Disable output of unescaped dangerous dynamic content;
- Do not expose sensitive information on the page;
- Disable retention of meaningless test markers,Debugging information and temporary placeholder content;
