*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/selenium.robot

Library  Selenium2Library  timeout=10  implicit_wait=0.5
Library  plone.app.robotframework.keywords.Debugging
Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Start browser
Suite Teardown  Close All Browsers

*** Variables ***

${BROWSER} =  firefox
${MANAGER} =  Manager

*** Test Cases ***

Plone site
    [Tags]  start
    Go to  http://localhost:55001/plone/
    Page should contain  Plone site
    Enable autologin as  ${MANAGER}
    Maximize Browser Window
    Reload Page
    CLick Link  user-name
    Click Link  ${PLONE_URL}/@@overview-controlpanel
    Click Link  ${PLONE_URL}/@@dexterity-types
    Click Element  add-type
    Input Text  form-widgets-title  dms document
    Input Text  form-widgets-description  document management system
    Click Element  form-buttons-add
    Go to  ${PLONE_URL}/dexterity-types/dms_document/@@behaviors
    Select Checkbox  form-widgets-collective-dms-scanbehavior-behaviors-behaviors-IScan-0
    Click Element  form-buttons-apply
    CLick Link  folder
    Click link  ${PLONE_URL}/folder/folder_factories
    CLick Link  dms_document
    Page Should Contain Link  fieldsetlegend-3
    Click Link  fieldsetlegend-3

*** Keywords ***

Start browser
    Open browser  http://localhost:55001/plone/  browser=${BROWSER}
