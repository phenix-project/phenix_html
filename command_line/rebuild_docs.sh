#!/bin/sh

if [ -z "$PHENIX" ]; then
  echo "PHENIX environment variable not set."
  exit 1
elif [ ! -d $PHENIX ]; then
  echo "PHENIX environment variable is set, but not a directory:"
  echo "  $PHENIX"
  exit 1
fi

PHENIX_HTML=`libtbx.find_in_repositories phenix_html`
if [ -z "$PHENIX_HTML" ]; then
  echo "$PHENIX_HTML not found; aborting"
fi

HTML_LOG=$1
if [ -z "$HTML_LOG" ]; then
  HTML_LOG=/dev/null
fi
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

cd $PHENOX_HTML
echo "Building PHENIX documentation in $PHENIX_HTML"
echo "The complete documentation will be in:"
echo "  $PHENIX/doc"

echo "  creating restructured text files"
cd $PHENIX_HTML/rst_files
phenix.python ../scripts/create_refinement_txt.py
phenix.python ../scripts/create_fmodel_txt.py

echo "  building HTML files from restructured text files"
for file in `ls *.txt` ; do
  disable=`grep -c "disable_rst2html" $file`
  if [ "$disable" = "0" ]; then
    echo "      converting $file to `echo $file | sed -e 's|.[^.]*$||'`.html"
    docutils.rst2html $file > `echo $file | sed -e 's|.[^.]*$||'`.html
  fi
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

cd $PHENIX_HTML
phenix.python $PHENIX/phenix/phenix/utilities/toc_and_index.py >> $HTML_LOG

echo "  populating documentation directory $PHENIX/doc"

if [ -d $PHENIX/doc ]; then
  /bin/rm -rf $PHENIX/doc
fi

mkdir -p $PHENIX/doc

cp -r $PHENIX_HTML/icons   $PHENIX/doc
cp -r $PHENIX_HTML/images  $PHENIX/doc
cp    $PHENIX_HTML/*.html  $PHENIX/doc
cp    $PHENIX_HTML/*.htm   $PHENIX/doc
/bin/rm $PHENIX/doc/phenix_documentation.html
VERSION=${PHENIX_VERSION}-${PHENIX_RELEASE_TAG}
sed "s/INSTALLED_VERSION/$VERSION/;" $PHENIX_HTML/phenix_documentation.html > $PHENIX/doc/phenix_documentation.html
ln -s $PHENIX/doc/phenix_documentation.html $PHENIX/doc/index.html

echo "done."

exit 0
