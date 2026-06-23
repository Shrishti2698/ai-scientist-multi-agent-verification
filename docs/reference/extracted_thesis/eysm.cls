%%
%% This is file `eysm.cls',
%% based on the `book.cls' file of the Standard LaTeX document class
%%
%% Written by Reinhard Furrer 08/2002
%% send any comments to furrer@ucar.edu 
%%
%% Copyright of the original `book.cls' file 1993 1994 1995 1996 1997 1998 1999
%% The LaTeX3 Project and any individual authors listed elsewhere
%% in this file.
%% 
%% 
%% This file may be distributed and/or modified under the
%% conditions of the LaTeX Project Public License, either version 1.2
%% of this license or (at your option) any later version.
%% The latest version of this license is in
%%    http://www.latex-project.org/lppl.txt
%% and version 1.2 or later is part of all distributions of LaTeX
%% version 1999/12/01 or later.
%% 
%% This file may only be distributed together with a copy of the LaTeX
%% base system. You may however distribute the LaTeX base system without
%% such generated files.
%% 
%% The list of all files belonging to the LaTeX base distribution is
%% given in the file `manifest.txt'. See also `legal.txt' for additional
%% information.
\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{eysm}
              [1999/09/10 v1.4a
 based on `book.cls' Standard LaTeX document class]
\newcommand\@ptsize{}
\newif\if@restonecol
\newif\if@openright
\newif\if@mainmatter \@mainmattertrue
\DeclareOption{a4paper}
   {\setlength\paperheight {297mm}%
    \setlength\paperwidth  {210mm}}
\DeclareOption{10pt}{\renewcommand\@ptsize{0}}
\DeclareOption{twoside}{\@twosidetrue  \@mparswitchtrue}
\DeclareOption{final}{\setlength\overfullrule{0pt}}
\DeclareOption{openright}{\@openrighttrue}
\DeclareOption{openany}{\@openrightfalse}
\DeclareOption{onecolumn}{\@twocolumnfalse}
\DeclareOption{leqno}{\input{leqno.clo}}
\DeclareOption{fleqn}{\input{fleqn.clo}}
\DeclareOption{openbib}{%
  \AtEndOfPackage{%
   \renewcommand\@openbib@code{%
      \advance\leftmargin\bibindent
      \itemindent -\bibindent
      \listparindent \itemindent
      \parsep \z@
      }%
   \renewcommand\newblock{\par}}%
}
\ExecuteOptions{a4paper,10pt,twoside,onecolumn,final,openright}
\ProcessOptions
\input{bk1\@ptsize.clo}
\setlength\lineskip{1\p@}
\setlength\normallineskip{1\p@}
\renewcommand\baselinestretch{}
\setlength\parskip{0\p@ \@plus \p@}
\@lowpenalty   51
\@medpenalty  151
\@highpenalty 301
\setcounter{topnumber}{2}
\renewcommand\topfraction{.7}
\setcounter{bottomnumber}{1}
\renewcommand\bottomfraction{.3}
\setcounter{totalnumber}{3}
\renewcommand\textfraction{.2}
\renewcommand\floatpagefraction{.5}
\setcounter{dbltopnumber}{2}
\renewcommand\dbltopfraction{.7}
\renewcommand\dblfloatpagefraction{.5}
\def\ps@headings{%
    \let\@oddfoot\@empty\let\@evenfoot\@empty
    \def\@evenhead{\thepage\hfil\slshape\leftmark}%
    \def\@oddhead{{\slshape\rightmark}\hfil\thepage}%
    \let\@mkboth\markboth
  \def\chaptermark##1{%
    \markboth {{%\MakeUppercase{%
      \ifnum \c@secnumdepth >\m@ne
        \if@mainmatter
          \@chapapp\ \thechapter. \ %
        \fi
      \fi
      ##1}}{}}%
  \def\sectionmark##1{%
    \markright {{%\MakeUppercase{%
      \ifnum \c@secnumdepth >\z@
        \thesection. \ %
      \fi
      ##1}}}}
\def\ps@myheadings{%
    \let\@oddfoot\@empty\let\@evenfoot\@empty
    \def\@evenhead{\thepage\hfil\slshape\leftmark}%
    \def\@oddhead{{\slshape\rightmark}\hfil\thepage}%
    \let\@mkboth\@gobbletwo
    \let\chaptermark\@gobble
    \let\sectionmark\@gobble
    }
\newcommand*\chaptermark[1]{}
\setcounter{secnumdepth}{2}
\newcounter {part}
\newcounter {chapter}
\newcounter {section}[chapter]
\newcounter {subsection}[section]
\newcounter {subsubsection}[subsection]
% \newcounter {paragraph}[subsubsection]
% \newcounter {subparagraph}[paragraph]
\renewcommand \thepart {\@Roman\c@part}
\renewcommand \thechapter {\@arabic\c@chapter}
\renewcommand \thesection {\@arabic\c@section}
\renewcommand\thesubsection   {\thesection.\@arabic\c@subsection}
\renewcommand\thesubsubsection{\thesubsection .\@arabic\c@subsubsection}
% \renewcommand\theparagraph    {\thesubsubsection.\@arabic\c@paragraph}
% \renewcommand\thesubparagraph {\theparagraph.\@arabic\c@subparagraph}
\newcommand\@chapapp{\chaptername}

\newcommand\chapter{\if@openright\cleardoublepage\else\clearpage\fi
                    \thispagestyle{plain}%
                    \global\@topnum\z@
                    \@afterindentfalse
\typeout{^^J^^J You should not use the chapter command. ^^J^^J}
                    \secdef\@chapter\@schapter}
\def\@chapter[#1]#2{\ifnum \c@secnumdepth >\m@ne
                       \if@mainmatter
                         \refstepcounter{chapter}%
                         \typeout{\@chapapp\space\thechapter.}%
                         \addcontentsline{toc}{chapter}%
                                   {\protect\numberline{\thechapter}#1}%
                       \else
                         \addcontentsline{toc}{chapter}{#1}%
                       \fi
                    \else
                      \addcontentsline{toc}{chapter}{#1}%
                    \fi
                    \chaptermark{#1}%
                    \addtocontents{lof}{\protect\addvspace{10\p@}}%
                    \addtocontents{lot}{\protect\addvspace{10\p@}}%
                    \@makechapterhead{#2}%
                    \@afterheading
                    }
\def\@makechapterhead#1{%
  \vspace*{50\p@}%
  {\parindent \z@ \raggedright \normalfont
    \ifnum \c@secnumdepth >\m@ne
      \if@mainmatter
        \huge\bfseries \@chapapp\space \thechapter
        \par\nobreak
        \vskip 20\p@
      \fi
    \fi
    \interlinepenalty\@M
    \Huge \bfseries #1\par\nobreak
    \vskip 40\p@
  }}
\def\@schapter#1{\@makeschapterhead{#1}%
  \@afterheading}
\def\@makeschapterhead#1{%
  \vspace*{50\p@}%
  {\parindent \z@ \raggedright
    \normalfont
    \interlinepenalty\@M
    \Huge \bfseries  #1\par\nobreak
    \vskip 40\p@
  }}
\newcommand\section{\@startsection {section}{1}{\z@}%
                                   {-3.5ex \@plus -1ex \@minus -.2ex}%
                                   {2.3ex \@plus.2ex}%
                                   {\normalfont\Large\bfseries}}
\newcommand\subsection{\@startsection{subsection}{2}{\z@}%
                                     {-3.25ex\@plus -1ex \@minus -.2ex}%
                                     {1.5ex \@plus .2ex}%
                                     {\normalfont\large\bfseries}}
\newcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%
                                     {-3.25ex\@plus -1ex \@minus -.2ex}%
                                     {1.5ex \@plus .2ex}%
                                     {\normalfont\normalsize\bfseries}}
% \newcommand\paragraph{\@startsection{paragraph}{4}{\z@}%
%                                     {3.25ex \@plus1ex \@minus.2ex}%
%                                     {-1em}%
%                                     {\normalfont\normalsize\bfseries}}
% \newcommand\subparagraph{\@startsection{subparagraph}{5}{\parindent}%
%                                        {3.25ex \@plus1ex \@minus .2ex}%
%                                        {-1em}%
%                                       {\normalfont\normalsize\bfseries}}
\setlength\leftmargini  {2.5em}
\leftmargin  \leftmargini
\setlength\leftmarginii  {2.2em}
\setlength\leftmarginiii {1.87em}
\setlength\leftmarginiv  {1.7em}
\setlength\leftmarginv  {1em}
\setlength\leftmarginvi {1em}
\setlength  \labelsep  {.5em}
\setlength  \labelwidth{\leftmargini}
\addtolength\labelwidth{-\labelsep}
\@beginparpenalty -\@lowpenalty
\@endparpenalty   -\@lowpenalty
\@itempenalty     -\@lowpenalty
\renewcommand\theenumi{\@arabic\c@enumi}
\renewcommand\theenumii{\@alph\c@enumii}
\renewcommand\theenumiii{\@roman\c@enumiii}
\renewcommand\theenumiv{\@Alph\c@enumiv}
\newcommand\labelenumi{\theenumi.}
\newcommand\labelenumii{(\theenumii)}
\newcommand\labelenumiii{\theenumiii.}
\newcommand\labelenumiv{\theenumiv.}
\renewcommand\p@enumii{\theenumi}
\renewcommand\p@enumiii{\theenumi(\theenumii)}
\renewcommand\p@enumiv{\p@enumiii\theenumiii}
\newcommand\labelitemi{\textbullet}
\newcommand\labelitemii{\normalfont\bfseries \textendash}
\newcommand\labelitemiii{\textasteriskcentered}
\newcommand\labelitemiv{\textperiodcentered}
\newenvironment{description}
               {\list{}{\labelwidth\z@ \itemindent-\leftmargin
                        \let\makelabel\descriptionlabel}}
               {\endlist}
\newcommand*\descriptionlabel[1]{\hspace\labelsep
                                \normalfont\bfseries #1}
\newenvironment{verse}
               {\let\\\@centercr
                \list{}{\itemsep      \z@
                        \itemindent   -1.5em%
                        \listparindent\itemindent
                        \rightmargin  \leftmargin
                        \advance\leftmargin 1.5em}%
                \item\relax}
               {\endlist}
\newenvironment{quotation}
               {\list{}{\listparindent 1.5em%
                        \itemindent    \listparindent
                        \rightmargin   \leftmargin
                        \parsep        \z@ \@plus\p@}%
                \item\relax}
               {\endlist}
\newenvironment{quote}
               {\list{}{\rightmargin\leftmargin}%
                \item\relax}
               {\endlist}
\setlength\arraycolsep{5\p@}
\setlength\tabcolsep{6\p@}
\setlength\arrayrulewidth{.4\p@}
\setlength\doublerulesep{2\p@}
\setlength\tabbingsep{\labelsep}
\skip\@mpfootins = \skip\footins
\setlength\fboxsep{3\p@}
\setlength\fboxrule{.4\p@}
\@addtoreset {equation}{chapter}
\renewcommand\theequation
  {\ifnum \c@chapter>\z@ \thechapter.\fi \@arabic\c@equation}
\newcounter{figure}[chapter]
\renewcommand \thefigure
     {\ifnum \c@chapter>\z@ \thechapter.\fi \@arabic\c@figure}
\def\fps@figure{tbp}
\def\ftype@figure{1}
\def\ext@figure{lof}
\def\fnum@figure{\figurename~\thefigure}
\newenvironment{figure}
               {\@float{figure}}
               {\end@float}
\newcounter{table}[chapter]
\renewcommand \thetable
     {\ifnum \c@chapter>\z@ \thechapter.\fi \@arabic\c@table}
\def\fps@table{tbp}
\def\ftype@table{2}
\def\ext@table{lot}
\def\fnum@table{\tablename~\thetable}
\newenvironment{table}
               {\@float{table}}
               {\end@float}
\newlength\abovecaptionskip
\newlength\belowcaptionskip
\setlength\abovecaptionskip{10\p@}
\setlength\belowcaptionskip{0\p@}
\long\def\@makecaption#1#2{%
  \vskip\abovecaptionskip
  \sbox\@tempboxa{#1: #2}%
  \ifdim \wd\@tempboxa >\hsize
    #1: #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}%
  \fi
  \vskip\belowcaptionskip}
\DeclareOldFontCommand{\rm}{\normalfont\rmfamily}{\mathrm}
\DeclareOldFontCommand{\sf}{\normalfont\sffamily}{\mathsf}
\DeclareOldFontCommand{\tt}{\normalfont\ttfamily}{\mathtt}
\DeclareOldFontCommand{\bf}{\normalfont\bfseries}{\mathbf}
\DeclareOldFontCommand{\it}{\normalfont\itshape}{\mathit}
\DeclareOldFontCommand{\sl}{\normalfont\slshape}{\@nomath\sl}
\DeclareOldFontCommand{\sc}{\normalfont\scshape}{\@nomath\sc}
\DeclareRobustCommand*\cal{\@fontswitch\relax\mathcal}
\DeclareRobustCommand*\mit{\@fontswitch\relax\mathnormal}
\newcommand\@pnumwidth{1.55em}
\newcommand\@tocrmarg{2.55em}
\newcommand\@dotsep{4.5}
\setcounter{tocdepth}{0}
\newcommand\tableofcontents{%
    \chapter*{\contentsname
        \@mkboth{%
           \MakeUppercase\contentsname}{\MakeUppercase\contentsname}}%
    \@starttoc{toc}%
    }
\newcommand*\l@part[2]{%
  \ifnum \c@tocdepth >-2\relax
    \addpenalty{-\@highpenalty}%
    \addvspace{2.25em \@plus\p@}%
    \begingroup
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      {\leavevmode
       \large \bfseries #1\hfil \hb@xt@\@pnumwidth{\hss #2}}\par
       \nobreak
         \global\@nobreaktrue
         \everypar{\global\@nobreakfalse\everypar{}}%
    \endgroup
  \fi}
\newcommand*\l@chapter[2]{%
  \ifnum \c@tocdepth >\m@ne
    \addpenalty{-\@highpenalty}%
    \vskip 1.0em \@plus\p@
    \setlength\@tempdima{1.5em}%
    \begingroup
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      \leavevmode \bfseries
      \advance\leftskip\@tempdima
      \hskip -\leftskip
      #1\nobreak\hfil \nobreak\hb@xt@\@pnumwidth{\hss #2}\par
      \penalty\@highpenalty
    \endgroup
  \fi}
\newcommand*\l@section{\@dottedtocline{1}{1.5em}{2.3em}}
\newcommand*\l@subsection{\@dottedtocline{2}{3.8em}{3.2em}}
\newcommand*\l@subsubsection{\@dottedtocline{3}{7.0em}{4.1em}}
% \newcommand*\l@paragraph{\@dottedtocline{4}{10em}{5em}}
% \newcommand*\l@subparagraph{\@dottedtocline{5}{12em}{6em}}
\newcommand*\l@figure{\@dottedtocline{1}{1.5em}{2.3em}}
\let\l@table\l@figure
\newdimen\bibindent
\setlength\bibindent{1.5em}
\newenvironment{thebibliography}[1]
     {\chapter*{\bibname
        \@mkboth{\MakeUppercase\bibname}{\MakeUppercase\bibname}}%
      \list{\@biblabel{\@arabic\c@enumiv}}%
           {\settowidth\labelwidth{\@biblabel{#1}}%
            \leftmargin\labelwidth
            \advance\leftmargin\labelsep
            \@openbib@code
            \usecounter{enumiv}%
            \let\p@enumiv\@empty
            \renewcommand\theenumiv{\@arabic\c@enumiv}}%
      \sloppy
      \clubpenalty4000
      \@clubpenalty \clubpenalty
      \widowpenalty4000%
      \sfcode`\.\@m}
     {\def\@noitemerr
       {\@latex@warning{Empty `thebibliography' environment}}%
      \endlist}
\newcommand\newblock{\hskip .11em\@plus.33em\@minus.07em}
\let\@openbib@code\@empty
\newenvironment{theindex}
               {%\if@twocolumn
%                   \@restonecolfalse
%                 \else
%                   \@restonecoltrue
%                 \fi
\typeout{^^J^^J You should not use the index environment. ^^J^^J}
                \columnseprule \z@
                \columnsep 35\p@
                \twocolumn[\@makeschapterhead{\indexname}]%
                \@mkboth{\MakeUppercase\indexname}%
                        {\MakeUppercase\indexname}%
                \thispagestyle{plain}\parindent\z@
                \parskip\z@ \@plus .3\p@\relax
                \let\item\@idxitem}
              {}
%               {\if@restonecol\onecolumn\else\clearpage\fi}
\newcommand\@idxitem{\par\hangindent 40\p@}
\newcommand\subitem{\@idxitem \hspace*{20\p@}}
\newcommand\subsubitem{\@idxitem \hspace*{30\p@}}
\newcommand\indexspace{\par \vskip 10\p@ \@plus5\p@ \@minus3\p@\relax}
\renewcommand\footnoterule{%
  \kern-3\p@
  \hrule\@width.4\columnwidth
  \kern2.6\p@}
\@addtoreset{footnote}{chapter}
\newcommand\@makefntext[1]{%
    \parindent 1em%
    \noindent
    \hb@xt@1.8em{\hss\@makefnmark}#1}
\newcommand\contentsname{Contents}
\newcommand\bibname{References}
\newcommand\indexname{Index}
\newcommand\figurename{Figure}
\newcommand\tablename{Table}
\newcommand\chaptername{Chapter}
\setlength\columnsep{10\p@}
\setlength\columnseprule{0\p@}
\pagestyle{empty}
\pagenumbering{arabic}
\onecolumn

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% personal macros enter here:
\newcommand\startup{
\usepackage[latin1]{inputenc}
\usepackage{a4,calc,amsmath,amsthm,amsfonts,ifthen,%
rotate,color,enumerate,fancyheadings}
\usepackage[pdftex]{graphicx}
\usepackage[english]{babel}


\makeatletter

%\renewcommand{\labelitemi}{{\scriptsize\bullet}}
%\renewcommand{\labelenumi}{{\rm\arabic}}
\renewcommand{\theequation}{\arabic{equation}}
\numberwithin{equation}{section}

\newdimen\breite         
\setlength{\breite}{25pt}
\newdimen\hohe            
\setlength{\hohe}{12pt}  

\addtolength{\textwidth}{4\breite}
\addtolength{\oddsidemargin}{-2\breite}
\addtolength{\evensidemargin}{-2\breite}
\addtolength{\textheight}{2\hohe}
\addtolength{\topmargin}{-2\hohe}


% definitions pour fancyheadings
\setlength{\headrulewidth}{.3pt}
\rhead[\fancyplain{}{\hspace*{2mm}\sffamily\footnotesize\nouppercase\leftmark}]{\fancyplain{}{\hspace*{2mm}\sffamily\bfseries \small\thepage}}
\lhead[\fancyplain{}{{\sffamily\bfseries \small\thepage}\hspace*{2mm}}]{\fancyplain{}{\sffamily\footnotesize\nouppercase \rightmark}}
\chead[\fancyplain{}{}]{\fancyplain{}{}}
\cfoot[]{\fancyplain{\small\sffamily\bfseries\thepage}{}}

\addtolength{\headheight}{2.5pt}
}

% definitions for glossary, which represents addresslist

\newenvironment{theglossary}{%
  \thispagestyle{plain}
  \chapter*{Address List of Authors}
  \list{}{%
    \setlength{\labelwidth}{0em}%
    \setlength{\leftmargin}{\labelwidth}%
    \addtolength{\leftmargin}{0em}%
  }%
}{% \endlist
}

% author information 
\newcommand{\name}[1]{\def\@name{#1}}
\newcommand{\firstname}[1]{\def\@firstname{#1}}
\newcommand{\affiliation}[1]{\def\@affiliation{#1}}
\newcommand{\country}[1]{\def\@country{#1}}
\newcommand{\email}[1]{\def\@email{#1}}
% coauthors information (at most 2 suppl. authors)
\newcommand{\stname}[1]{\def\@stname{#1}}
\newcommand{\stfirstname}[1]{\def\@stfirstname{#1}}
\newcommand{\staffiliation}[1]{\def\@staffiliation{#1}}
\newcommand{\stcountry}[1]{\def\@stcountry{#1}}
\newcommand{\stemail}[1]{\def\@stemail{#1}}

\newcommand{\ndname}[1]{\def\@ndname{#1}}
\newcommand{\ndfirstname}[1]{\def\@ndfirstname{#1}}
\newcommand{\ndaffiliation}[1]{\def\@ndaffiliation{#1}}
\newcommand{\ndcountry}[1]{\def\@ndcountry{#1}}
\newcommand{\ndemail}[1]{\def\@ndemail{#1}}

% coauthor informations
\def\coauthornumber#1{\def\@coauthornumber{#1}}
\def\ceins{1}\def\czwei{2}


\def\@initname#1#2{\@@initname#1#2\delimiter}
\def\@@initname#1#2#3\delimiter{\def#1{#2}}
\@initname{\@ndaname}{Furrer}


\newcommand{\@printauthor}[4]{{\Large\sc#1~#2}\\[1mm]\normalsize#3\\{\tt#4}\\[5mm]}

% print authoraddress and coauthors
\newcommand{\printauthor}{\@printauthor{\@name}{\@firstname}{\@affiliation}{\@email}\setcounter{section}{0}%
\ifx\@coauthornumber\ceins{\@printauthor{\@stname}{\@stfirstname}{\@staffiliation}{\@stemail}}\fi%
\ifx\@coauthornumber\czwei{\@printauthor{\@stname}{\@stfirstname}{\@staffiliation}{\@stemail}%
\@printauthor{\@ndname}{\@ndfirstname}{\@ndaffiliation}{\@ndemail}}\fi\vspace*{8mm}}

% article information
\renewcommand{\title}[1]{\def\@title{#1}}
\newcommand{\runninghead}[1]{\def\@runninghead{#1}}

\newcommand{\acknowledgements}[1]{\def\@acknowledgements{#1}}
\newcommand{\keywords}[1]{\def\@keywords{#1}}

\newcommand{\EYSMabstract}[1]{\def\@eysmabstract{#1}}
\newcommand{\EYSMarticle}[1]{\def\@eysmarticle{#1}}



% write headings of abstracts and articles
\newcommand{\abstractend}{%
\smallskip\par\noindent{\sc Keywords}:~\@keywords
\ifx\@acknowledgements\ceins{}\else{\smallskip\par\noindent{\sc Acknowledgements}:~\@acknowledgements}\fi}



\newcommand{\writeabstract}{\thispagestyle{plain}\LARGE{\begin{center}{\bf\@title}\\[2mm]\printauthor\end{center}}
\normalsize\addcontentsline{toc}{chapter}{\bfseries{\@name:}
    {\mdseries\@runninghead}}\index{\@name}\glossary{\@name~\@firstname\\\@affiliation\\\@country}\@eysmabstract\abstractend\newpage}


\newcommand{\articleend}{\cleardoublepage}

\newcommand{\writearticle}{\thispagestyle{plain}\LARGE{\begin{center}{\bf\@title}\\[2mm]\printauthor\end{center}}%
\normalsize\def\leftmark{\@runninghead}\def\rightmark{\@name~\@firstname}\addcontentsline{toc}{chapter}{\bfseries{\@name:}
    {\mdseries\@runninghead}}\index{\@name}\@eysmabstract\abstractend\bigskip\@eysmarticle}


% small macro to create ABSTRACT and ARTICLE page
\newcommand{\breakpart}[1]{
\cleardoublepage
\vspace*{5cm}\hspace*{8cm}{\Huge\bf#1}
\addtocontents{toc}{\protect \vspace*{6mm}}
\addcontentsline{toc}{chapter}{\bfseries{#1}}
\addtocontents{toc}{\protect \vspace*{3mm}}
\newpage~\cleardoublepage}



\let\oldcaption=\caption
\def\caption[#1]#2{\par\centerline{\parbox{\textwidth-30pt}{\oldcaption[#1]{\small#2}}}}

\renewenvironment{thebibliography}
   {\section{\bibname}\let\bibitem\item
     \begin{list}
     {}
     {
       \setlength{\labelwidth}{0em}
       \setlength{\itemindent}{-1em}
       \setlength{\leftmargin}{1em}
       \setlength{\itemsep}{0cm}
     } 
   }
   {\end{list}}

\newcommand\appendix{\par
  \setcounter{chapter}{0}%
  \setcounter{section}{0}%
\typeout{^^J^^J You should not use the appendix environment. ^^J^^J}
  \gdef\@chapapp{\appendixname}%
  \gdef\thesection{\@Alph\c@section}}

% that's it
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% initalize variables:
\acknowledgements{1}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\endinput
%%
%% End of file `eysm.cls'.
