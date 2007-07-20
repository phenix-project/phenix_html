text=open("good_list").read()
good_lines=text.split("\n")
text=open("list1.dat").read()
all_lines=text.split("\n")
for line in all_lines:
  if line and line.replace(" ","") and not line in good_lines:
     print line
