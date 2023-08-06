#!/bin/bash
# ------------------------------------------------------------------------------
# cd "$(dirname "${BASH_SOURCE[0]}")"
wd="$(pwd)"
sd="$(dirname "${BASH_SOURCE[0]}")"

# ------------------------------------------------------------------------------
# Print usage instructions
function usage {
    echo "---------------------------------------------------------"
    echo "Sprites.sh"
    echo "---------------------------------------------------------"
    echo "Makes sprites from a folder of images."
    echo "Needs python 2.6 or newer."
    echo ""
    echo ""
    echo "      -i, --input             The directory containing all the sprite directories (this thang is recursive)"
    echo "      -o, --ouput             The sprite image ouput directory"
    echo "      -c, --css               CSS output directory"      
    echo "      -s, --sass              Directory where the generated CSS will be produced."
    echo "      -f, --file              Filename of output css. Default: _sprites.scss"
    echo "      -t, --testpage_dir      Directory to create the HTML test page in. Default: current dir"
    echo "      -n, --testpage_name     The HTML name of the test page. Default: sprite_test_page.html"
    echo "      -h, --help              By jove, you're here already."
    echo ""
}

function directoryHints {
    echo -e "\033[31mNo images found. Drop your sprite images in a sub-folder for each pixel aspect ratio."
    echo -e "\033[90mEg: sprites/"
    echo "          base/           (the 1x has no prefix)"
    echo "          base-0.75x/     (smaller than 1x for poxy androids)"
    echo "          base-1.5x/      (android pseudo-retina)"
    echo -e "          base-2x/        (true retina)\033[0m"
}

# ------------------------------------------------------------------------------
# Generate HTML test page
function renderTestPage {
    temp=$SASS_FILE".temp"
    temp2=$SASS_FILE".temp2"
    
    rm -f $temp2 $sprite_test_page
    
    replaceThisPath=$(python -c "import os.path; print os.path.relpath('$sprite_output_dir', '$sprite_css_output_dir')" )
    withThisPath=$(python -c "import os.path; print os.path.relpath('$sprite_output_dir', '$sprite_test_page_dir')" )
    # strip the CSS images paths out, and replace them with a path relative
    # to the location of the sprites_test_page.html
    # 
    styles=$(cat $SASS_FILE | sed -e "s@$replaceThisPath@$withThisPath@g")

    mkdir -p "$sprite_test_page_dir"

    # Make an HTML test page.
    html="<!doctype html>
<html>
    <head>
        <title>Sprite test sheet</title>
        <style type='text/css'>
            body{
                font-family:sans-serif;
                color: #333;
                background-image: url(data:image/png;base64,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);
            }
            .sprite_list{
                list-style:none;
            }
            .sprite_list li {
                margin-bottom: 1em;
                padding-bottom: 1em;
                border-bottom: solid 1px #eee;
            }
            .sprite_list li > p {
                font-size: .875em;
            }
            .test_sprite{
                display:block;
            }
            
            $styles

        </style>
    </head>
    <body>
        <!-- sprites -->
        <ul class='sprite_list'>
"

    # parse the lines out into a file via a Glob.
    while read line
    do
        if [[ "$line" = .* ]]
            then
            echo "${line//[\.\{\,]/}" >> $temp;
        fi    
    done < "$SASS_FILE"

    # Sort the lines
    awk '!x[$0]++' $temp > $temp2

    # read the lines back in and make a div for each of the selectors.
    while read line
    do
        html+="        <li>
                <p>.$line</p>
                <div class='test_sprite $line'></div>
            </li>
    "
    done < $temp2

    rm -f $temp $temp2

    html+="     </ul><!-- end sprites -->
    </body>
</html>"

    # Save the test page
    echo "$html" > $sprite_test_page

    echo -e "\033[90mTest page: \033[4m$sprite_test_page\033[0m"
}

# ------------------------------------------------------------------------------
# Make sure python is 2.6 or later
function pythonOk {
PYTHON_OK=`python -c 'import sys
print (sys.version_info >= (2, 6) and "1" or "0")'`

    if [ "$PYTHON_OK" = '0' ]; then
        echo ""
        echo "Oops. Sprites requires python 2.6 or higher."
        echo "http://www.python.org/getit/"
        echo ""
        exit
    fi
}

# ------------------------------------------------------------------------------
# Compress sprites if user has pngcrush
function crushSprites {
    fat_sprites=($sprite_output_dir/sprite_*.png)

    echo -e "\033[90mSqueezing with PNGCrush\033[0m"
    for _sprite in ${fat_sprites[@]}; do
        pngcrush -s -rem alla -reduce $_sprite $_sprite".tmp"
        mv -f $_sprite".tmp" $_sprite
    done
}

# ------------------------------------------------------------------------------
# What it says on the tin.
function createOutputCSSFile {
temp_css_files=$(ls $TEMP_CSS_FILES 2> /dev/null | wc -l)
    operatingSystem=$(uname -s)
    
    if [ "$temp_css_files" -gt "0" ]
        then
            # Concat the CSS into a single file
            rm -f $SASS_FILE
            printf "/**\n * ----------------------------------------\n * Sprites\n * ----------------------------------------\n */\n\n" > $SASS_FILE

            # for OSX use sort -n
            if [ "$operatingSystem" == "Darwin" ]; then
                (ls -d $TEMP_CSS_FILES | sort -n -t _ -k 2 | xargs cat) >> $SASS_FILE
            fi;

            # for Linux, use sort -V
            if [ "$operatingSystem" == "Linux" ]; then
                (ls -d $TEMP_CSS_FILES | sort -V -t _ -k 2 | xargs cat) >> $SASS_FILE
            fi;

        # Clean up after that damn cat
        rm -f $TEMP_CSS_FILES
        else
            echo -e "\033[31mSorry, couldn't find any output CSS. Exiting.\033[0m"
            exit
    fi
}

# ------------------------------------------------------------------------------
# What it says on the tin.
function createSprites {
    for _ief in $sprite_input_dir/*; do
        if [ -e "$_ief" ]; then

            files=(`find $_ief -maxdepth 1 -name "*.png"`)

            if [ ${#files[@]} -gt 0 ]; 
                then 
                    # echo $_ief
                    # echo $sprite_css_output_dir
                    # echo $sprite_sass_output_dir
                    # echo $sprite_output_dir
                    pypacker -i "$_ief" -c "$sprite_css_output_dir" -a "$sprite_sass_output_dir" -s "$sprite_output_dir"  -m grow --test
                else
                    echo "\033[90mSkipping $_ief because it's empty. Put some .png images in the directory to make a sprite.\033[0m"
            fi
        else
            echo -e "\033[31mYou need images to make a sprite, fool.\033[0m"
        fi
    done
}

# ------------------------------------------------------------------------------
# What it says on the tin.
function init {
    subdircount=0
    if [ -d "$sprite_input_dir" ]; then
        subdircount=$(find "$sprite_input_dir" -maxdepth 1 -type d | wc -l)
    fi

    if [ $subdircount -ge 2 ]; then
        nothing=''
    else
        directoryHints
        exit
    fi

    createSprites

    if hash pngcrush 2>/dev/null; then
        crushSprites
    else
        echo "Consider installing pngcrush for leaner sprites"
    fi

    createOutputCSSFile
    
    if [ -n "$didCreateOutputCSS" ]
        then
        something=''
    fi

    if [[ -n $sprite_test_page ]]
    then
        renderTestPage
    fi
}

function setDefaults {
    # The image input directory
    sprite_input_dir="images/sprites";

    # Where images are output
    sprite_output_dir="images";

    # Where CSS is served from. This is used to work out the background-url
    # relative to the CSS_DIR.
    sprite_css_output_dir="css";

    # Where SaSS expects to find the sprite CSS
    sprite_sass_output_dir="";

    # What the concatenated sprite css file is called
    sprite_sass_file="_sprites.scss"

    # a test page to review all the sprites in one handy place
    sprite_test_page_dir=$wd
    sprite_test_page_name="cheat_sheet.html"
}

# Before starting, check for config and correct python version
pythonOk
setDefaults

# echo ${@}

while [ "$1" != "" ]; do

    case $1 in
        -i | --input )          shift
                                dir=$1
                                if [ -z "$dir" ]; then 
                                    dir="../"
                                fi
                                sprite_input_dir="$dir"
                                ;;
        -o | --output )         shift
                                if [ -z "$dir" ]; then 
                                    dir="../"
                                fi
                                sprite_output_dir="$1"
                                ;;
        -c | --css )            shift
                                sprite_css_output_dir="$1"
                                ;;
        -s | --sass )           shift
                                sprite_sass_output_dir="$1"
                                ;;
        -f | --file )           shift
                                sprite_sass_file="$1"
                                ;;
        -t | --testpage_dir )   shift 
                                sprite_test_page_dir="$1"
                                ;;
        -n | --testpage_name )  shift
                                sprite_test_page_name="$1"
                                ;;                       
        -h | --help )           usage
                                exit 1
                                ;;
    esac
    shift
done

# Internal vars
# 
# actual name of sprite test page.
sprite_test_page=$sprite_test_page_dir/"$sprite_test_page_name"

if [ "$sprite_sass_output_dir" == "" ]
    then
    TEMP_CSS_FILES="$sprite_css_output_dir"/*.css.temp
    sprite_sass_output_dir="$sprite_css_output_dir"
fi

SASS_FILE=$sprite_sass_output_dir/${sprite_sass_file}
TEMP_CSS_FILES=$sprite_sass_output_dir/*.css.temp

# echo "$sprite_test_page_name"
# echo $TEMP_CSS_FILES
# echo $SASS_FILE
# echo $sprite_sass_output_dir


# Go
init