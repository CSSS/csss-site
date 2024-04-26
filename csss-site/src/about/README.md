# Officer App

## Responsible for
 - [1. Store SFU Officer Position Info](#1-store-sfu-officer-position-info)
   - [1.1. How `OfficerEmailListAndPositionMapping` is used when storing a new/repeat officer's data](#11-how-officeremaillistandpositionmapping-is-used-when-storing-a-newrepeat-officers-data)
     - [1.1.1. Explanation of Table](#111-explanation-of-table)
   - [1.2. How Director of Archives generates `UnProcessedOfficer`](#12-how-director-of-archives-generates-unprocessedofficer)
     - [1.2.1. Explanations of input fields](#121-explanations-of-input-fields)
     - [1.2.2. Validations Performed](#122-validations-performed)
     - [1.2.3. Additional Processing](#123-additional-processing)
       - [1.2.4. Things I never got around to doing](#124-things-i-never-got-around-to-doing)
   - [1.3. When officer inputs their info](#13-when-officer-inputs-their-info)
     - [1.3.1. How various Officer objects are obtained that are not obtained directly from user](#131-how-various-officer-objects-are-obtained-that-are-not-obtained-directly-from-user)
     - [1.3.2. Validations](#132-validations)
     - [1.3.3. Upon Successful Validation of all Inputs](#133-upon-successful-validation-of-all-inputs)
     - [1.3.4. SFU Maillist Management](#134-sfu-maillist-management)
       - [1.3.4.1. How the csss-doa can login to manage the maillists](#1341-how-the-csss-doa-can-login-to-manage-the-maillists)
       - [1.3.4.2. Maillist Management Logic](#1342-maillist-management-logic)
         - [1.3.4.2.1. Who goes in what mailist?](#13421-who-goes-in-what-mailist)
         - [1.3.4.2.2. How to remove someone from an announcement maillist](#13422-how-to-remove-someone-from-an-announcement-maillist)
         - [1.3.4.2.3. How to setup the permissions for an officer maillist](#13423-how-to-setup-the-permissions-for-an-officer-maillist)
         - [1.3.4.2.4. How does the csss-doa get access to all the maillists?](#13424-how-does-the-csss-doa-get-access-to-all-the-maillists)
         - [1.3.4.2.5. Why does `csss-doa` not follow the convention of the other maillists with who is a member?](#13425-why-does-csss-doa-not-follow-the-convention-of-the-other-maillists-with-who-is-a-member)
         - [1.3.4.2.6. Why did the 2017 SysAdmin and Director of Archived setup `csss-doa` as the moderator of the maillists?](#13426-why-did-the-2017-sysadmin-and-director-of-archived-setup-csss-doa-as-the-moderator-of-the-maillists)
         - [1.3.4.2.7. Things I never got around to doing](#13427-things-i-never-got-around-to-doing)
       - [1.3.4.3. How to read the graphics below?](#1343-how-to-read-the-graphics-below)
     - [1.3.5. Regarding Bitwarden Management](#135-regarding-bitwarden-management)
     - [1.3.6. Things I never got around to doing](#136-things-i-never-got-around-to-doing)
 - [2. Keeping track of non-SFU email addresses for announcements](#2-keeping-track-of-non-sfu-email-addresses-for-announcements)
 - [3. Officer List](#3-officer-list)
   - [3.1. Publicly Accessible Data](#31-publicly-accessible-data)
   - [3.2. Sensitive Data exposed only to current or recent executives](#32-sensitive-data-exposed-only-to-current-or-recent-executives)
   - [3.3. Things I never got around to updating](#33-things-i-never-got-around-to-updating)
 - [4. Background Cron Commands](#4-background-cron-commands)
   - [4.1. Nag DoA to Generate Links](#41-nag-doa-to-generate-links)
   - [4.2. Nag officers to enter their info](#42-nag-officers-to-enter-their-info)
   - [4.3. Updating Discord Details](#43-updating-discord-details)
   - [4.4. Updating Officer Images](#44-updating-officer-images)
   - [4.5. Validation of Discord Roles](#45-validation-of-discord-roles)

# 1. Store SFU Officer Position Info

## 1.1. How `OfficerEmailListAndPositionMapping` is used when storing a new/repeat officer's data

https://sfucsss.org/about/officer_position

Officer I decided have/don't have access during my term to certain resources

| Position Index | Position Name                | SFU Maillist                  | Elected via Election Officer | Github Access | Google Drive Access | Executive | Election officer | SFSS Council Representative | Frosh Week Chair | Discord Manager | Discord Role Name              | Number of Relevant Terms | Starting Month |
|----------------|------------------------------|-------------------------------|------------------------------|---------------|---------------------|-----------|------------------|-----------------------------|------------------|-----------------|--------------------------------|--------------------------|----------------|
| 0              | President                    | csss-president-current@sfu.ca | True                         | True          | True                | True      | False            | False                       | False            | False           | President                      | 3                        | Summer         |
| 1              | Vice-President               | csss-vp-current@sfu.ca        | True                         | True          | True                | True      | False            | False                       | False            | False           | Vice President                 | 3                        | Summer         |
| 2              | Treasurer                    | csss-treasurer-current@sfu.ca | True                         | True          | True                | True      | False            | False                       | False            | False           | Treasurer                      | 3                        | Summer         |
| 3              | Director of Resources        | csss-dor-current@sfu.ca       | True                         | True          | True                | True      | False            | False                       | False            | False           | Director of Resources          | 3                        | Summer         |
| 4              | Director of Events           | csss-doe-current@sfu.ca       | True                         | True          | True                | True      | False            | False                       | False            | False           | Director of Events             | 3                        | Summer         |
| 5              | Director of Education Events | csss-doee-current@sfu.ca      | True                         | True          | True                | True      | False            | False                       | False            | False           | Director of Educational Events | 3                        | Summer         |
| 6              | Assistant Director of Events | csss-adoe-current@sfu.ca      | True                         | True          | True                | True      | False            | False                       | False            | False           | Assistant Director of Events   | 3                        | Summer         |
| 7              | Director of Communications   | csss-doc-current@sfu.ca       | True                         | True          | True                | True      | False            | False                       | False            | False           | Director of Communications     | 3                        | Summer         |
| 8              | Director of Multi-media      | csss-domm-current@sfu.ca      | True                         | True          | True                | True      | False            | False                       | False            | False           | Director of Multi-Media        | 3                        | Summer         |
| 9              | Director of Archives         | csss-doa-current@sfu.ca       | True                         | True          | True                | True      | False            | False                       | False            | False           | Director of Archives           | 3                        | Summer         |
| 10             | Executive at Large 1         | csss-eal-current@sfu.ca       | False                        | True          | True                | True      | False            | False                       | False            | False           | Exec at Large                  | 1                        | None           |
| 11             | Executive at Large 2         | csss-eal-current@sfu.ca       | False                        | True          | True                | True      | False            | False                       | False            | False           | Exec at Large                  | 1                        | None           |
| 12             | First Year Representative 1  | csss-fyr-current@sfu.ca       | False                        | True          | True                | True      | False            | False                       | False            | False           | First Year Rep                 | 2                        | Fall           |
| 13             | First Year Representative 2  | csss-fyr-current@sfu.ca       | False                        | True          | True                | True      | False            | False                       | False            | False           | First Year Rep                 | 2                        | Fall           |
| 14             | General Election Officer     | csss-elections@sfu.ca         | False                        | False         | False               | False     | True             | False                       | False            | False           | Elections Officer              | 1                        | Spring         |
| 15             | By-Election Officer          | csss-elections@sfu.ca         | False                        | False         | False               | False     | True             | False                       | False            | False           | Elections Officer              | 1                        | None           |
| 16             | SFSS Council Representative  | csss-councilrep@sfu.ca        | True                         | False         | True                | False     | False            | True                        | False            | False           | CSSS Council Representative    | 3                        | Summer         |
| 17             | Frosh Week Chair             | csss-froshchair@sfu.ca        | False                        | True          | True                | False     | False            | False                       | True             | False           | Frosh Chair                    | 3                        | Spring         |
| 18             | Systems Administrator        | csss-sysadmin@sfu.ca          | False                        | True          | True                | False     | False            | False                       | False            | False           | CSSS Sys Admin                 | None/Infinite            | None/Infinite  |
| 19             | Webmaster                    | csss-webmaster@sfu.ca         | False                        | True          | True                | False     | False            | False                       | False            | False           | NA                             | None/Infinite            | None           |
| 20             | CSSS Discord Manager         | NA                            | False                        | True          | False               | False     | False            | False                       | False            | True            | CSSS Discord Manager           | None/Infinite            | None           |

### 1.1.1. Explanation of Table
When I first started working on this website, there was a need for a way to keep track of 
1. **email**: the SFU maillist associated with the position
1. **position_index**: what the order in which the position should appear in on the list of officers and on the election pages

as a result, to keep track of these bits of info, I created the model `OfficerEmailListAndPositionMapping`.

> When the phrase "processing an `UnProcessedOfficer`" below, that translates to "when an new/repeat officer is filling in their information"

However, overtime, the need for the thing to keep track of grew to
1. **discord_role_name**: the name of the discord role to assign to an officer when processing an `UnProcessedOfficer`.
1. **github**: an indicator of whether the system need to obtain a new officer's github username when processing a new `UnProcessedOfficer` as the officer needs to have access to the [CSSS officers team](https://github.com/orgs/CSSS/teams/officers)
1. **google_drive**: an indicator of whether the system needs to obtain a new officer's gmail when processing a new `UnProcessedOfficer` as the officer needs to have access to the [CSSS@SFU](https://drive.google.com/drive/folders/0AGb0FPdVjrsqUk9PVA) and maybe [Deep-Exec](https://drive.google.com/drive/folders/0AEthg-w3Ogz7Uk9PVA) and [Private Gallery](https://drive.google.com/drive/folders/1cKOkFTDfu_6GqqbaYrPVqstb-H-HzMdX).
1. **marked_for_deletion**: this was originally added so that if during a term, a position get removed from the constitution, then the position can be accordingly marked for deletion and would be deleted from the system once the term is over. Just to be clear, the `OfficerEmailListAndPositionMapping` entry where **marked_for_deletion** is set to `True` would be deleted and not any of the officers recorded with the marked position.
1. **elected_via_election_officer**: As the `elections` app uses `OfficerEmailListAndPositionMapping` to get a list of officer positions that a nominee can select that they want to run for, there needed to be a way to ensure that only position that are elected via an election held by an election officer are offered as options to a nominee. This is where this flag's usefulness comes in.
1. **executive_officer**: This is used in number of ways. 
   1. used to ensure that someone is not holding 2 executive positions at the same time in the same term
   2. used as a flag to know when to send someone the introductory email/discord DM that is tailed for executives
   3. determine if the user should be placed in the discord role `Execs`
   4. Some details on the webpages should only be shown if the user occupied an executive position in a given time period. This flags helps to narrow that down  
1. **election_officer**: used as a flag to know when to send someone [the introductory email/discord DM that is tailed for the election officer](views/input_new_officers/enter_new_officer_info/notifications/create_intro_message.py)
1. **sfss_council_rep**: used as a flag to know when to send someone [the introductory email/discord DM that is tailed for the SFSS Council Rep](views/input_new_officers/enter_new_officer_info/notifications/create_intro_message.py)
1. **frosh_week_chair**: used as a flag to know when to send someone [the introductory email/discord DM that is tailed for the Frosh Week Chair](views/input_new_officers/enter_new_officer_info/notifications/create_intro_message.py)
1. **discord_manager**: used as a flag to know when to send someone [the introductory email/discord DM that is tailed for the Discord Manager](views/input_new_officers/enter_new_officer_info/notifications/create_intro_message.py)
 
In addition, there are 2 attributes that exist in `OfficerEmailListAndPositionMapping` that I never got around to adding to the website just cause I didn't get a chance to update that page:
1. **shared_position**: as some positions [like Frosh Week Chair] can be held by more than 1 people sometimes [like if there is a tie and the potential chairs are OK with holding the position together], then this flag is used by the process that stores a new officer's info, so it knows when it's valid for a position to be shared, cause otherwise, it wil assume an error happened that resulted in a position being specified more than once
1. **bitwarden_access**: Used just to alert the Director of Archives to tell the Sys Admin perform a take-over of the bitwarden account for the SFU maillist associated with the position once the Director of Archives updates the members of the SFU maillist.

An explanation of the resource permission management can be found in the [`Resource Management app`](../resource_management)

## 1.2. How Director of Archives generates `UnProcessedOfficer`
<img src="https://docs.google.com/drawings/d/e/2PACX-1vTYsdFf2P5EiQrNwqNOYNGXOc0-E9fgUgw2mOIfSNc8WE3kSBuYuwew3w60W5HO91-WfrfqpowlZZkC/pub?w=564&amp;h=331">  

The way I coded the site, each new term, all officers have to enter their information, regardless of whether they are a new officer or are just continuing to serve a term until its fullest [for example, any of the Director positions in the Fall or Spring term]

Shortly before the new term, the Director of Archives had to create a new `UnProcessedOfficer` object, that they would create those entries via https://sfucsss.org/about/specify_new_officers

Once the Director of Archives fills out the below form, in order to motivate/ensure repeat officers do fill in their info again for the new term, the website uses the [`UnProcessedOfficer` model in order to keep ensure that officers who have not filled in their form cannot access the SFU CSSS Google Drive, the SFU CSSS Github Org, and are not given their discord exec role](../csss/views/privilege_validation/list_of_officer_details_from_past_specified_terms.py)

![](https://github.com/CSSS/csss-site/blob/add_docu/csss-site/src/about/documentation_images/generate_unprocessedofficer.png)

### 1.2.1. Explanations of input fields
Most fields in the above screenshot are pretty intuitive, however
 * **Number of Nags so Far**: what I found was that officers tend to procrastinate with filling in their links [at least prior to tying management of the discord officer roles to whether or not they had filled in their links]. As a result, I created a [cron service](management/commands/nag_officers_to_enter_info.py) that DMs an officer using a custom cron trigger until they fill in their links.
 * **Start Date**: So the way I coded the website was that the start_date of an officer is the date that they got elected or appointed to the position. So if a Director stuck with a position through to the end of their term, their started date for all three of their `Officer` objects for that particular run all share the same start date but have different term object. Hence why the `Officer did not have to be voted into position again this term` checkbox exists, so that the Director of Archives can just click that instead of having to interact with the date field at the beginning of every Fall and Spring term for all the Director positions that need have links created
 * **Overwrite Current Officer**: I disabled that, it was stupid logic but just never got around to removing it from the front-end.

### 1.2.2. Validations Performed
The website ensures that the `SFU Computing ID` inputted by the Director of Archives is valid via API `GET https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/amaint/namespace.json?id=<sfu_computing_id>&art=<SFU_API_TOKEN>`


### 1.2.3. Additional Processing
If the specified position has gmail access, a unique gmail verification code is generated and saved to the officer to later on validate their inputted gmail

### 1.2.4. Things I never got around to doing
 * Send the Director of Archives repeat reminders before the term ends to generate the links if the system doesn't detect the typical officers as existing for next term nor does it detect the needed `UnProcessedOfficer` objects needed for the next term
 * Giving the Director of Archives the option to select a past officer rather than have to manually fill in an officer's name, discord ID and sfu computing ID
 * Making the page smarter about giving the Director of Archives the option to select a button that would automatically generate the typical position links that would be needed for a term. For example, at the end of a term, it would know that all exec positions and the First year Rep would need to be generated so it gives the Director of Archives the option to create that many empty Officer inputs rather than them having to click the `Add Another New officer` button 10+ times

## 1.3. When officer inputs their info
<img src="https://docs.google.com/drawings/d/e/2PACX-1vT1W611KG5uXME5gK-IvUbK0srFRNmxomRmznLGeZDV7T1PkBNhHNKgEXd1GtpBImJH9-qkqmEhf6aH/pub?w=1702&amp;h=1121">

https://sfucsss.org/login?next=/about/enter_new_officer_info

![](https://github.com/CSSS/csss-site/blob/add_docu/csss-site/src/about/documentation_images/enter_officer_info.png)

### 1.3.1. How various Officer objects are obtained that are not obtained directly from user
* **sfu_computing_id**: pulled from the corresponding `UnProcessedOfficer` object
* **sfu_email_alias**: obtained via `GET https://rest.its.sfu.ca/cgi-bin/WebObjects/AOBRestServer.woa/rest/datastore2/global/accountInfo.js?username=<sfu_computing_id>&art=<SFU_API_TOKEN>`
* **phone_number**: obtained via the form, but I believe it **is** possible to get the number they have on file with SFU, just never got around to asking SFU IT to adding it to the list of details we get about a student upon validating them with the API endpoint `GET https://cas.sfu.ca/cas/p3/serviceValidate?service=https://sfucsss.org&ticket=<ticket>`
* **discord_username**: obtained via `GET https://discord.com/api/guilds/{GUILD_ID}/members/{discord_id}`
* **discord_nickname**: obtained via `GET https://discord.com/api/guilds/{GUILD_ID}/members/{discord_id}`
* **image**: Please look below at section [Updating Officer Images](#updating-officer-images)
* **elected_term**: pulled from the corresponding `UnProcessedOfficer` object
* **sfu_officer_mailing_list_email**: pulled from corresponding `OfficerEmailListAndPositionMapping` object
* **bitwardern_takeover_needed** | **bitwarden_is_set**: just ignore what logic I actually implemented and attempt to implement what I was going for in [Regarding Bitwarden Management](#regarding-bitwarden-management)

### 1.3.2. Validations
1. gmail:
   1. regex validation performed
   2. the website sends an email to the specified gmail with the code in `UnProcessedOfficer` object for that user and asks the user to enter that code, to ensure they have access to the gmail
2. github username
   1. validated using `GET https://api.github.com/search/users?q=<github_username>&per_page=1`

### 1.3.3. Upon Successful Validation of all Inputs
Once that all clears, the website
1. Enforces the permission management outlined in [`Resource Management app`](../resource_management#13-code-workflow-when-officer-inputs-their-information)
1. Ensuring the corresponding CSSS Discord Roles are properly assigned.
1. sends the Director of Archives an email letting them know that they may need to update the members of an SFU maillist. See []() for more details
1. And finally sending them both an email and discord DM with links to documentation that is hopefully useful
    1. [intro message creation](views/input_new_officers/enter_new_officer_info/notifications/create_intro_message.py)

### 1.3.4. SFU Maillist Management

##### 1.3.4.1. How the csss-doa can login to manage the maillists
**the Director of Archives can log into https://maillist.sfu.ca/ using their own username `csss:<sfuid>` [and not `csss`] to manage the maillists**  

Once the officer enters their info, the Director of Archives is emailed to update the mappings and are referred to https://sfucsss.org/about/current_email_mappings, which handles the logic of figuring out who goes where. An explanation of the logic is provided below
![](https://github.com/CSSS/csss-site/blob/add_docu/csss-site/src/about/documentation_images/csss_maillist_mappings.png)

#### 1.3.4.2. Maillist Management Logic
* All Officer [except the one below] have a main [`-current`] maillist and a secondary maillist.
  * `csss-elections`
  * `csss-councilrep`
  * `csss-sysadmin`
  * `csss-webmaster`
##### 1.3.4.2.1. Who goes in what mailist?
  * **main [`-current`] maillist**: the person currently holding a position goes in the main maillist. This is indicated in the graphics below with the bolding that is shown in the **maillist members** section of a main maillist
  * **secondary maillist**: the main maillist as well as the previous person to occupy that position [assuming the previous person was a different person]. This is indicated in the graphics below with the bolding that is shown in the **maillist members** section of the secondary maillist

##### 1.3.4.2.2. How to remove someone from an announcement maillist
Some mailists are populated by the FAS Office, such maillists are: 
1. any that are prefixed with `cmpt-`, which is currently just `cmpt-students`
2. any `csss-` maillists that are owned by `csilops`, which is currently just `csss-firstyears`

All other maillists are owned and operated by the CSSS and their members are updated only by the CSSS.

##### 1.3.4.2.3. How to setup the permissions for an officer maillist
If you are setting up a maillist whose members should be restricted to certain people, You will need to set the following subscription policy:
![](https://github.com/CSSS/csss-site/blob/add_docu/csss-site/src/about/documentation_images/subscription_settings_restricted_maillist.png)

* the reason that the first option in the dropdown can't work is obvious
* the second option doesn't work cause even if the owner/manager hasn't yet approved a member, that member will still start getting emails sent to that maillist.

##### 1.3.4.2.4. How does the csss-doa get access to all the maillists?
![](https://github.com/CSSS/csss-site/blob/add_docu/csss-site/src/about/documentation_images/csss_doa_maillist_moderator.png)

So this is a hack that was discovered by the 2017 Director of Archives and Sys administrator but basically, the moderator of a maillist was technically supposed to be an option to only SFUIDs.
**However**, due either to laziness or technical limitations, the way that the system ensures that a selected option for a moderator is an SFUID is **not** by actually making sure it is an SFUID, it's by checking the number of characters in the option. Hence since `csss-doa` happens to be <= 8 in character length, we can use it as a moderator for the maillist sytems :smile:  
As a result, 

##### 1.3.4.2.5. Why does `csss-doa` not follow the convention of the other maillists with who is a member?
As opposed to the other maillists that have the current officer as a member via the `-current` maillist, `csss-doa` has the current Director of Archives directly as a member rather than via another maillist.
This is because as `csss-doa` is a manager for all the other maillists, only direct members of the `csss-doa` maillist get that managerial privilege. That level of control does not extend to member of maillists that are members of the `csss-doa` maillist.

An alternative could have been to make a maillist called `csss-mod` and have that be the manager for all the other maillists, but I got too lazy to set that up just so that `csss-doa`'s members follow the convention that the other maillists have.

##### 1.3.4.2.6. Why did the 2017 SysAdmin and Director of Archived setup `csss-doa` as the moderator of the maillists?
Doing it this way, when there is a change in Director of Archives, you are not stuck updating the moderator of 20+ maillists. All you have to do is updating the member of `csss-doa`.

##### 1.3.4.2.7. Things I never got around to doing
I am 99.9% sure that updating the maillist **can** actually be automated. Since the maillist does not have a complete API [as stated in the email below], this can **technically** be accomplished with the usage of [request](https://pypi.org/project/requests/)'s [Session](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects) object, but I realized this only in the last year of my time as a Sys Admin and had other things to take care of so never implemented this automation.
![](https://github.com/CSSS/csss-site/blob/add_docu/csss-site/src/about/documentation_images/lack_of_automation_support.png)


#### 1.3.4.3. How to read the graphics below?
Just a visual representation of what I tried to say above. the bolded members of a maillist illustrate members that a Director of Archives may have to update. Any maillists that don't have any bolded members don't need to be updated.

Additionally, `csss-doa` is green to indicate both that
* it's the maillist used to maintain all the other maillists as well as
* its maillists members are different than the pattern found in other non `-current` maillists.

<img src="https://docs.google.com/drawings/d/e/2PACX-1vRa13F_U-XuEMM4pkPbFKHS5BjuEp0TSKzNs-ugZBom36OL09yJLFxedjdI8nKapfTTGY7E2oXLTi1s/pub?w=3284&amp;h=7784">

### 1.3.5. Regarding Bitwarden Management
> When doing a take-over of a bitwarden account, that account gets it access to any Bitwarden Organization Colletion or Groups removed. To deal with that, I had to implement a bit of a fix that is elaborated on in [`Resource Management app`](../resource_management)  

Regarding the bitwarden attributes, I suggest ignoring whatever logic there is and just re-implementing the logic, **but** what I was attempting to implement was that: If there is a change in who is occupying a position that has a bitwarden account, once the Director of Archives updates that position's `-current` maillist, then the Sys Admin is alerted to that fact and they take-over the account on bitwarden and use the website to generate and send the new password to that officer on the discord. I suggest having the website itself DM the password to the new officer to make it seem more automated but :shrug:

### 1.3.6. Things I never got around to doing
 * I had always planned that when the last executive officer inputs their information at the beginning of every term, that the website would send the updated exec-list to the maillists that the Director of Archives always has to send to.

# 2. Keeping track of non-SFU email addresses for announcements
<img src="https://docs.google.com/drawings/d/e/2PACX-1vQgtlJHOKOKnkLYbXyplGjtwwVFEGlTxq3HjylcFvmaLCntfPnoa7MZ3JQHLJMAL6uJz_AbB8UKYQqs/pub?w=1080&amp;h=765">

In order to ensure that only "verified" emails sent to csss.website@gmail.com are shown on the front page, the website has to know which sender emails are valid ones to show. For the most part the SFU email addresses [both SFUID and email aliases] are tracked via the Officer's own info and are commonly the sender email. but there have been occasions where folks have used non-SFU emails [like Gmails] to send emails to the student body. As a result the `AnnouncementEmailAddress` model was created to track those valid non-SFU email addresses.

# 3. Officer List

When it comes to the officers list page [https://sfucsss.org/about/list_of_current_officers] and [https://sfucsss.org/about/list_of_past_officers]
what is shown is pretty self-explanatory between being anonymous and being a validated current or recent executive<sup>1</sup>

## 3.1. Publicly Accessible Data
* Name
* Discord Nickname
* Discord Username
* Favorite Courses
* Favorite Languages
* Contact Email
* Bio

## 3.2. Sensitive Data exposed only to current or recent executives
* SFUID
* Phone Number
* Github Username
* Gmail

## 3.3. Things I never got around to updating
* Updating the contact details for an officer so that the contact email is shown using below logic [Using `President` role for example]:
  * `csss-president-current@sfu.ca` is shown only for the current President
  * `csss-president@sfu.ca` is shown for both the current and the previous President.
* I had always wanted to create an additional page where certain specified officer info can be displayed in a table format which can be easily downloaded as a csv file.
 

# 4. Background Cron Commands
There are some regular services that I have running regularly in the bckground via the [`cron service`](../csss/views/crons) I implemented in `csss`

## 4.1. Nag DoA to Generate Links
[nag_doa_to_generate_links.py](management/commands/nag_doa_to_generate_links.py)
Reminds the Director of Archives to generate the officer Links before the end of the term since once the next term starts, only the root user can do it

## 4.2. Nag officers to enter their info
[nag_officers_to_enter_info.py](management/commands/nag_officers_to_enter_info.py)  
Service was created to remind officers to enter their info

## 4.3. Updating Discord Details
[update_discord_details.py](management/commands/update_discord_details.py)  
Is used to update all the discord usernames and nicknames associated with any `Officer` object that have a valid `discord_id` so that https://sfucsss.org/about/list_of_current_officers and https://sfucsss.org/about/list_of_past_officers can have the latest discord details

## 4.4. Updating Officer Images
[validate_discord_roles_members.py](management/commands/update_officer_images.py)  
So the way that the officer images are set is via [csss-site-exec-photos](https://github.com/CSSS/csss-site-exec-photos) repo  
what basically happens is that when I was given all the exec photos taken for a term, I would dump all of them into the [Exec_Photos CSS Shared Team Drive](https://drive.google.com/drive/folders/1Rxfcmk3ntDLwcu9v9fUpVB1yDWiMLnKw), then I would take the ones that each officer requested be used for them and add those images to the [csss-site-exec-photos](https://github.com/CSSS/csss-site-exec-photos) repo. 

And in order to save up on the disk space taken by the repo, I would use short links `ln -s` as much as possible if a photo is re-used.

Once a photo is saved to that repo, the logic in [validate_discord_roles_members.py](management/commands/update_officer_images.py) would [do a `git pull` in the folder on the server that has that repo](https://github.com/CSSS/csss-site/blob/6a61fc1eac3f125ac865c22c410d8fff9bf77f44/csss-site/src/about/views/commands/update_officer_images.py#L14-L25) and then go through [this logic](https://github.com/CSSS/csss-site/blob/add_docu/csss-site/src/about/views/utils/get_officer_image_path.py) for each officer to get the correct image path or just revert to the stock photo if no image is found for that specific officer for that specific term. 

## 4.5. Validation of Discord Roles
[validate_discord_roles_members.py](management/commands/validate_discord_roles_members.py)  
This service was created to ensure that no matter what the Moderators/Minions play around with/do on discord, the roles are always updated at the end of the day to reflect what is shown on https://sfucsss.org/about/list_of_current_officers so that any officer who have no yet filled in their info, are motivated to do so 


<sup>1</sup>An explanation of which recent executives continue to have access to sensitive data can be found in the [`Resource Management app`](../resource_management)