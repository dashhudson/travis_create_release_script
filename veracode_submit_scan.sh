#!/bin/bash
# Executing this script will zip the repo and submit it to veracode for static analysis

# Installing dependencies
# We use python and node images depending on the repo. the node images appear to have
#       issues with the most recent version of httpie, so to combat this an older version
#       is downloaded if the python version is not sufficient. 
sudo snap install xmlstarlet
if [ "$TRAVIS_PYTHON_VERSION" >= "3.0" ]; then
    echo "Triggering python build"
    pip install httpie
    pip install veracode-api-signing
else 
    echo "Triggering node build"
    sudo pip install httpie==0.9.9
    sudo pip install veracode-api-signing
fi


# Getting a list of all our apps present in veracode and saving it as an XML
http --auth-type=veracode_hmac "https://analysiscenter.veracode.com/api/5.0/getapplist.do" > applist.xml
cat applist.xml

# Parsing the XML for the `app_id` where `app_name == $STACK_NAME`
export APP_ID=$( xmlstarlet sel -N oe="http&#x3a;&#x2f;&#x2f;www.w3.org&#x2f;2001&#x2f;XMLSchema-instance" -N ve="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applist" xsi:schemaLocation="https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;schema&#x2f;2.0&#x2f;applist https&#x3a;&#x2f;&#x2f;analysiscenter.veracode.com&#x2f;resource&#x2f;2.0&#x2f;applist.xsd" --net -t -v '//*[@app_name="'$STACK_NAME'"]/@app_id' -n applist.xml )
echo "This app's veradoce ID: "$APP_ID

# zip all .py .js .vue files except those in /tests/ or /__tests__/
# TODO: May be useful to implement a `.veracodeignore` or something similar to allow
#       developers to specify files that shouldn't be scanned.
zip -R veracode_submission.zip \
                '*.py' '*.js' '*.vue' 'requirements.txt' 'package-lock.json' 'Pipfile.lock' \
                -x /**\*tests/**\* /**\*__tests__/**\* /**\*node_modules/**\* /**\*cypress/**\*

echo "Uploading file"
http --ignore-stdin --auth-type=veracode_hmac -f "https://analysiscenter.veracode.com/api/5.0/uploadfile.do" "app_id==$APP_ID" "file@veracode_submission.zip"

# Begin pre-scan
# With auto_scan=true the full scan will be triggered after the pre-scan using the veracode default modules
echo "Triggering scan"
http --auth-type=veracode_hmac "https://analysiscenter.veracode.com/api/5.0/beginprescan.do" "app_id==$APP_ID" "auto_scan==true"