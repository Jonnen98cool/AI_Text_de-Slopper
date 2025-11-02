#This program has ironically been created with the help of chatGPT


import sys

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
BLUE = "\033[94m"

REPLACEMENTS = {
    "—": "-",       #The dreaded emdash gets converted into a regular dash
    "’": "'",
    "“": '"',
    "”": '"',
    ',"': '",',     #Commas at the end of quotes are now placed outisde the quote. Conversion occurs after the ” --> " conversion
    "…": "...",     #Convert the triple dot character into three individual dots
   u"\u00A0": " "   #Convert non-breaking space into a regular space
    #"×": "*",      #You can go into various symbols as well
    #"é": "e",      #To go above and beyond maybe it would be good to handle cases like "résumé" --> "resume", but this is not always a desired change
}



def visualize_newlines(line):
    line = line.replace("\r\n", "__CRLF__")                   #Temporarily protect \r\n so the upcoming "\n" replacement doesn't hit twice
    line = line.replace("\n", f"{BLUE}\\n{RESET}")            #UNIX-style line breaks
    line = line.replace("__CRLF__", f"{BLUE}\\r\\n{RESET}")   #Windows-style line breaks
    return line


#Returns one change suggestion
def highlight_change(line, old, new, pos):
    old_representation = old
    new_representation = new
    if(old == u"\u00A0"):  #Make the non breaking space conversion more obvious
        old_representation = "\\u00A0"
        new_representation = "SPACE"

    before = line[:pos] + f"{RED}{old_representation}{RESET}" + line[pos + len(old):]
    before = visualize_newlines(before)
    after  = line[:pos] + f"{GREEN}{new_representation}{RESET}" + line[pos + len(old):]
    after = visualize_newlines(after)
    return before + "   -->   " + after


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 transform_file.py <filename>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)

    changed_lines = []
    new_text = text

    for old, new in REPLACEMENTS.items():
        start = 0
        while True:
            idx = new_text.find(old, start)
            if idx == -1:   #Loop until no more occurences of that character
                break
            #Show small context around the change
            left = max(0, idx - 20)
            right = min(len(new_text), idx + 20)
            snippet = new_text[left:right]

            rel_idx = idx - left  #Calculate relative position of the match in the snippet
            changed_lines.append(highlight_change(snippet, old, new, rel_idx))
            start = idx + 1
        new_text = new_text.replace(old, new)

    if not changed_lines:
        print("No replacing necessary, file is already clean.")
        return

    print("\nProposed changes:\n")
    for line in changed_lines:
        print(line)
    print()

    confirm = input("Apply these changes? (Y/n): ").strip().lower()
    if confirm in ("y", ""):  #User can enter Y, y or nothing (i.e. just pressing ENTER)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("Changes written to file.")
    else:
        print("No changes made.")



if __name__ == "__main__":
    main()
