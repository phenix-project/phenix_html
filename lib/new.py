from __future__ import print_function
#cat ../phenix_index.htm | grep '<li>' | grep -v '<li><A' > list1.dat
all_lines=[]
txt=open('../../../doc/phenix_index.html').read()
txt=txt.replace("<ul>","\n<ul>")
txt=txt.replace("<li>","\n<LI>")
txt=txt.replace("</li>","</LI>")
txt=txt.replace("<LI><a","<LI><A")

for line in txt.splitlines():
  if line and line.find("<LI>")>-1 and not line.find("<LI><A")>-1:
    all_lines.append(line.replace("<LI>","").replace("\n",""))

text=open("good_list").read()
good_lines=text.split("\n")
f=open('all_list','w')
for line in all_lines:
  f.write(line+"\n")
  if line and line.replace(" ","") and not line in good_lines:
     print(line)
