*** Settings ***

Resource  Selenium2Screenshots/keywords.robot
Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Test Setup  Run keywords  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Variables ***

${SSDIR}  /tmp/images


*** Keywords ***
a Site Owner
    Log in as site owner

a French Plone site
    Go to  ${PLONE_URL}/@@language-controlpanel
    Select From List  form.default_language  fr
    Click Button  form.actions.save

Mail configured
    Go to  ${PLONE_URL}/@@mail-controlpanel
    Input text  form.smtp_host  localhost
    Input text  form.smtp_port  9025
    Input text  form.email_from_name  Administrateur
    Input text  form.email_from_address  admin@monportail.fr
    Click Button  form.actions.save

Add user to plone site
    [Arguments]   ${fullname}  ${username}
    Go to  ${PLONE_URL}/@@usergroup-userprefs
    Wait until page contains element  css=form.link-overlay
    Click button  css=form.link-overlay .add
    Overlay is opened
    Wait Until Page Contains Element  zc.page.browser_form
    Input text  form.fullname  ${fullname}
    Input text  form.username  ${username}
    Input text  form.email  ${username}@example.com
    Input text  form.password  ${username}
    Input text  form.password_ctl  ${username}
    Unselect Checkbox  form.mail_me
    Click button  form.actions.register

Close Overlay
    Click Element  css=div.overlay div.close

Overlay should close
    Wait until keyword succeeds  60  1  Element should not remain visible  id=exposeMask
    Wait until keyword succeeds  60  1  Page should not contain element  css=div.overlay

Overlay is opened
    Wait Until Page Contains Element  css=.overlay

Add new
    [Arguments]   ${name}
    Open Add New Menu
    Click link  css=#plone-contentmenu-factories a#${name}
    Wait Until Page Contains Element  css=#form

I add a workspace
    Go to  ${PLONE_URL}
    Add new  workspace
    Input text  form-widgets-IBasic-title  Mon espace de travail
    Click Button    form-buttons-save
    Capture and crop page screenshot  ${SSDIR}/add_workspace.png  portal-column-content

I add a workspace member
    [Arguments]   ${fullname}  ${username}  ${group_id}
    Go to  ${PLONE_URL}/mon-espace-de-travail/@@sharing
    Click link  new-user-link
    Overlay is opened
    Wait Until Page Contains Element  zc.page.browser_form
    Input text  form.fullname  ${fullname}
    Input text  form.username  ${username}
    Input text  form.email  ${username}@example.com
    # form.roles
    Unselect checkbox  form.roles.3
    Select checkbox  form.groups.${group_id}
    Capture and crop page screenshot  ${SSDIR}/${username}.png  css=.overlay
    Click button  form.actions.register
    Overlay should close

I add a workspace group
    [Arguments]   ${name}  ${title}  ${description}  ${local_role_id}
    Click link  new-group-link
    Overlay is opened
    Wait Until Page Contains Element  createGroup
    Input text  addname  ${name}
    Input text  title  ${title}
    Input text  description:text  ${description}
    Select checkbox  form.localroles.${local_role_id}
    Capture and crop page screenshot  ${SSDIR}/${name}.png  css=.overlay
    Submit form  createGroup
    Overlay should close


*** Test cases ***

Generate screenshots
    Given a Site Owner
    And a French Plone site
    And Mail configured
    Add user to plone site  Pierre Durand  pdurand

    I add a workspace
    Open Add New Menu
    Wait until page contains  Document
    Capture and crop page screenshot  ${SSDIR}/add_new_menu.png  plone-contentmenu-factories  css=#plone-contentmenu-factories dd.actionMenuContent

    Click link  css=#contentview-local_roles a
    Capture and crop page screenshot  ${SSDIR}/sharing.png  portal-column-content

    I add a workspace group  contributeurs  Contributeurs  Contributeurs de l'espace de travail  0
    I add a workspace group  moderateurs  Modérateurs  Modérateurs de l'espace de travail  1
    I add a workspace group  lecteurs  Lecteurs  Lecteurs de l'espace de travail  3

    I add a workspace member  Jean Dupont  jdupont  1
    I add a workspace member  Marie Durand  mdurand  0

    # add an existing user to workspace
    Go to  ${PLONE_URL}/mon-espace-de-travail/@@sharing
    Input text  sharing-user-group-search  Pierre
    Click button  sharing-search-button
    Wait until page contains  Pierre Durand
    Capture and crop page screenshot  ${SSDIR}/search_user.png  css=#content-core form

    # add user to group
    Click link  css=ul#groups-list li:first-child a
    Overlay is opened
    Capture and crop page screenshot  ${SSDIR}/add_user_to_group_before.png  css=.overlay
    Input text  searchstring  Pierre
    Click button  css=.overlay input[name='form.button.Search']
    Wait until page contains element  css=.overlay input[value='pdurand']
    Select checkbox  css=.overlay input[value='pdurand']
    Click button  css=.overlay input[name='form.button.Add']
    Wait until page contains element  css=.info
    Capture and crop page screenshot  ${SSDIR}/add_user_to_group_after.png  css=.overlay
    Close Overlay


    Click link  css=#contentview-sendtolisting a
    Capture and crop page screenshot  ${SSDIR}/sendto.png  portal-column-content
    Input text  mailing_list_email_subject  Message aux contributeurs
    Select checkbox  Contributor.selectButton
    Execute javascript  tinyMCE.getInstanceById('email_body').setContent("<p>Bonjour,</p><p>Vous pouvez désormais ajouter des documents à cet <strong>espace de travail</strong>.</p><p>Merci,</p><p>Le responsable de l'espace</p>")
    Capture and crop page screenshot  ${SSDIR}/mail_written.png  portal-column-content

    Click link  css=#contentview-userlisting a
    Capture and crop page screenshot  ${SSDIR}/members.png  portal-column-content
