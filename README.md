**_Polls API project_**



**Models**

Poll

Choice

Vote

Topic

Pollster(User)

Follow

 
**Endpoints**

POST api/register - Creates a new user and a new authentication token

POST api/login - Authenticates and logs in a user and returns the authentication Token

GET api/polls - Gets the list of all polls

POST api/polls - Creates a new poll

GET api/polls/:id - Gets a poll of  a specified id

PUT api/polls/:id - Edits a poll of a specified id

DELETE api/polls/:id - Delete a poll of a specified id

GET api/polls/:id/tags - Gets the tags of the choice of the specified poll

DELETE api/polls/:id/tags/:id - Deletes the specified tag

POST api/polls/:id/tags - Creates a new tag for the specified choice of a specific poll

GET api/polls/:id/choices - Gets all the choices of that specific poll

POST api/polls/:id/choices - Creates a new choice for that specific poll

GET api/polls/:id/choices/:c_id - Gets a specific choice from a specific poll

PUT api/polls/:id/choices/:c_id - Edits the choice of a specific poll

DELETE api/polls/:id/choice/:c_id - Deletes a choice of a specific poll

GET api/polls/:id/choice/:c_id/votes - Gets all the votes of that specific poll

POST api/polls/:id/choice/:c_id/votes - Creates a new vote for that choice of that specific poll

GET api/polls/:id/chart

GET api/pollsters - Returns all the registered pollsters

GET api/pollsters/:id - Returns details on a specific pollster

GET api/pollsters/:id/follow - Follow a pollster with the specified id

GET api/pollsters/:id/unfollow - Unfollow a pollster with the specified id

GET api/pollsters/:id/followers- Lists out  the pollsters who follow that pollster

GET api/pollsters/:id/following- Lists out the pollsters that the pollster with the specified id follows




**Constraints**

Only signed out users can register

Only signed out user can login

Only logged in Pollsters can access the application

A poll can have a maximum of 5 choices

Only the creator of the poll can edit or delete a poll

Only  the creator of a poll can edit or delete a choice or view the choice details

Only the creator of a poll can view or delete tags of the poll

A Pollster can only vote for a poll once

Only authenticated Pollsters can vote

Only authenticated Users can get the chart of a poll


A pollster can not follow or be followed twice

A pollster can not unfollow/follow him/herself

A pollster can only see his/her personal details

**Tests**

All the tests have been integrated in the tests.py file

**Documentation**

You can visit the uri /api/documentation/ to view the full documentation