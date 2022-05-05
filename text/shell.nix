with import <nixpkgs> {};
  mkShell {
    buildInputs = [
      pdftk
      (texlive.combine {
        inherit (texlive) scheme-basic beamer luatex
          collection-latex bibtex
          xetex collection-xetex
          collection-latexrecommended collection-luatex collection-pictures
          collection-langcyrillic collection-fontsrecommended
          filehook import microtype ms polyglossia svg unicode-math xunicode
          Asana-Math standalone
          hyphenat framed lastpage multirow ednotes totcount titling bigfoot oberdiek mdframed needspace
          enumitem ulem metafont mfware soul titlesec upquote pbox tocloft
          elocalloc environ forest trimspaces mathpartir ucs was footmisc 
          draftwatermark everypage bold-extra
          fncychap tabulary threeparttable wrapfig capt-of eqparbox makecell vmargin
          varwidth latexmk xindy xurl
          fixcmex times graphicx-psmin latexdiff listings;
      })
      pandoc
    ];
  }
