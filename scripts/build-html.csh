#! /bin/csh -f

set phenix=`libtbx.find_in_repositories phenix`
set phenix_html=`libtbx.find_in_repositories phenix_html`

cd "$phenix_html/rst_files"
if ($status != 0) exit $status
phenix.python ../scripts/create_refinement_txt.py
phenix.python ../scripts/create_fmodel_txt.py

echo "  building HTML files from restructured text files"

foreach file ( `ls *.txt` )
  echo "    converting $file to $file:r.html"
  docutils.rst2html "$file" > "$file:r.html"
end

echo "  converting restructured text HTML files to raw HTML files"

foreach file ( `ls *.html` )
  echo "      converting $file to $file:r.raw"
  phenix.python ../scripts/raw_from_rst_html.py "$file" > "$file:r.raw"
  if ( ! $status ) then
    mv "$file:r.raw" "../raw_files"
  endif
end

echo "  converting raw HTML files, creating tables-of-contents, and indexing"

cd "$phenix_html"

phenix.python "$phenix/phenix/utilities/toc_and_index.py"
