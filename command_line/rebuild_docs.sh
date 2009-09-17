#!/bin/sh

if [ ! -d $PHENIX/phenix_html ]; then
  echo "$PHENIX/phenix_html not found; aborting"
fi

HTML_LOG=/var/tmp/phenix_html.log
for arg in $*; do
  case $arg in
  --log=*)
    log_tmp=`echo $arg | awk 'BEGIN{FS="="}{print $2}'`
    if [ -z "$log_tmp" ]; then
      echo "Error: Usage: phenix_html.rebuild_doc [--log=log.txt]"
      exit 1
    else
      HTML_LOG=$log_tmp
    fi
    ;;
  esac
done

cd $PHENIX/phenix_html
echo "Building PHENIX documentation"

echo "  creating restructured text files"
cd rst_files
phenix.python ../scripts/create_refinement_txt.py

echo "  building HTML files from restructured text files"
for file in `ls *.txt` ; do
  echo "      converting $file to `echo $file | sed -e 's|.[^.]*$||'`.html"
  docutils.rst2html $file > `echo $file | sed -e 's|.[^.]*$||'`.html
done


echo "  converting restructured text HTML files to raw HTML files"
for file in `ls *.html` ; do
  echo "      converting $file to `echo $file | sed -e 's|.[^.]*$||'`.raw"
  phenix.python ../scripts/raw_from_rst_html.py $file > `echo $file | sed -e 's|.[^.]*$||'`.raw
  if [ $? -eq 0 ]; then
    mv `echo $file | sed -e 's|.[^.]*$||'`.raw ../raw_files
  fi
done

echo "  converting raw HTML files, creating tables-of-contents, and indexing"

cd $PHENIX/phenix_html
phenix.python $PHENIX/phenix/phenix/utilities/toc_and_index.py >> $HTML_LOG

echo "  populating documentation directory $PHENIX/doc"

if [ -d $PHENIX/doc ]; then
  /bin/rm -rf $PHENIX/doc
fi

mkdir -p $PHENIX/doc

cp -r $PHENIX/phenix_html/icons   $PHENIX/doc
cp -r $PHENIX/phenix_html/images  $PHENIX/doc
cp    $PHENIX/phenix_html/*.html  $PHENIX/doc
cp    $PHENIX/phenix_html/*.htm   $PHENIX/doc
/bin/rm $PHENIX/doc/phenix_documentation.html
VERSION=${PHENIX_VERSION}-${PHENIX_RELEASE_TAG}
sed "s/INSTALLED_VERSION/$VERSION/;" $PHENIX/phenix_html/phenix_documentation.html > $PHENIX/doc/phenix_documentation.html
ln -s $PHENIX/doc/phenix_documentation.html $PHENIX/doc/index.html

echo "done."

exit 0
