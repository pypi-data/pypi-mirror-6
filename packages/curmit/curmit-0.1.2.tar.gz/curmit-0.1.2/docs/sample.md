<!-- curmit: https://docs.google.com/document/d/1cmphl-IBFF-aRcj6n9TZ37YXJMBfmnzPiAGgPNzVjNE/pub?embedded=true -->



# A Sample File

The contents of this file are hosted as a Google Document, which is published
to the web.

### The Flag

To flag this file for `curmit`, the following comment is placed at the
beginning of this Markdown file:

    <!-- curmit: https://docs.google.com/document/d/1cmphl-IBFF-aRcj6n9TZ37YXJMBfmnzPiAGgPNzVjNE/pub?embedded=true -->  
See the raw text
[here](https://raw2.github.com/jacebrowning/curmit/master/docs/sample.md).

### Automatic Update

To synchronize this file with the published content:

    curmit  
Which does the following:

 1. searches the tree for files containing "flags"  
 2. grabs the URL contents for each flagged file as text  
 3. replaces the file contents after the flag  
 3. commits/pushes the new contents using `git`
