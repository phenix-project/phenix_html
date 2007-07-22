#cat ../phenix_index.htm | grep '<LI>' | grep -v '<LI><A' > list1.dat
all_lines=[]
for line in open('../phenix_index.htm').readlines():
  if line and line.find("<LI>")>-1 and not line.find("<LI><A")>-1:
    all_lines.append(line.replace("<LI>","").replace("\n",""))

text=open("good_list").read()
good_lines=text.split("\n")
f=open('all_list','w')
for line in all_lines:
  f.write(line+"\n")
  if line and line.replace(" ","") and not line in good_lines:
     print line
