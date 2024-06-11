import re 

text = "This tutorial teaches you all you need to know to be able to craft powerful time-saving regular expressions. It starts with the most basic concepts, so that you can follow this tutorial even if you know nothing at all about regular expressions yet.The tutorial doesn’t stop there. It also explains how a regular expression engine works on the inside and alerts you to the consequences. This helps you to quickly understand why a particular regex does not do what you initially expected. It will save you lots of guesswork and head scratching when you need to write more complex regexes. Basically, a regular expression is a pattern describing a certain amount of text. Their name comes from the mathematical theory on which they are based. But we will not dig into that. You will usually find the name abbreviated to \"regex\" or \"regexp\". This tutorial uses \"regex\", because it is easy to pronounce the plural \"regexes\". On this website, regular expressions are shaded gray as regex. This first example is actually a perfectly valid regex. It is the most basic pattern, simply matching the literal text regex. A “match” is the piece of text, or sequence of bytes or characters that pattern was found to correspond to by the regex processing software. Matches are highlighted in blue on this site. \b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b is a more complex pattern. It describes a series of letters, digits, dots, underscores, percentage signs and hyphens, followed by an at sign, followed by another series of letters, digits and hyphens, finally followed by a single dot and two or more letters. In other words: this pattern describes an email address. This also shows the syntax highlighting applied to regular expressions on this site. Word boundaries and quantifiers are blue, character classes are orange, and escaped literals are gray. You’ll see additional colors like green for grouping and purple for meta tokens later in the tutorial. With the above regular expression pattern, you can search through a text file to find email addresses, or verify if a given string looks like an email address. This tutorial uses the term “string” to indicate the text that the regular expression is applied to. This website highlights them in green. The term “string” or “character string” is used by programmers to indicate a sequence of characters. hello-world@coucou.net In practice, you can use regular expressions with whatever data you can access using the application or programming language you are working with."

# find all occurence in text
pattern = r"regex"
pattern = r"reg(ular expressions?|ex(p|es)?)"
out = re.findall(pattern=pattern, string=text)
print(out)

# return a Match object
out = re.search(pattern=pattern, string=text)
print(out.start())
print(text[out.start():out.start()+len(pattern)])

# find an email address:
# pattern = r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
pattern = r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"
out = re.findall(pattern=pattern, string=text)
print(out)

# replace
pattern = r"reg(ular expressions?|ex(p|es)?)"
out = re.sub(pattern=pattern, repl="HELLOOOOOOOOOOOOOOOOO", string=text)
print(out)