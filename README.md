# jbl-chat

Let's set the stage, you are the founder of this exciting new messaging startup, you are tasked with building the first version of a product that is aimed to evolve with feedback from the team and users.

You're building the backend using Django, and your initial task is to leverage HTMX for interactive front-end experiences. With this first release, we want to deliver the following user stories:

1. As a user, I want to see all other users on the platform.
2. As a user, I want to view my conversation with another user.
3. As a user, I want to be able to send messages to another user on the platform.

Given that this is your startup, you have the freedom to set up and utilize the practices that align with your goals. You can use any Python libraries or external tools that you prefer.

We have provided a Django skeleton project along with Docker setup for your convenience. Feel free to utilize Docker for development or Python virtual environments for your local setup. Since managing user registration isn’t required for this assessment, you can create dummy users directly using the shell and implement session authentication.

Incorporating HTMX will allow you to create dynamic, interactive elements on the front end without needing to reload the page. We encourage you to think about how HTMX can enhance user interactions effectively.

Happy coding!

# Thoughts by dimo

## Conversation
The `Conversation` object, is it needed? Basically, if we're simply implementing messaging between 2 people,
we don't need a `Conversation`, but if we ever want to make groups or anything like that, it makes sense that
every conversation, even one between two people is it's own container.
It does make things a little more complicated and I probably don't need it in this example.

## Message storage and security
Should messages be a single message object with a `Conversation` connection or should each message be replicated
with a direct connection to the user it was meant for, and a connection to a "root" message that can be used
for editing - if someone edits a message, it's children can be updated. Deletion would also work in such a way,
if a user deletes a message locally, we might not always want that deletion to propagate to all message
recipients.

From a security pov it's probably good to make separate messages for every recipient, this would
also be better from a legal PoV where messages could be stored in the target user's locale etc.
It makes it harder for messages to find their way into another user's mailbox by making the target
field immutable in the code.
The connection to the root message can also be deleted after a while, ensuring that uesrs can not
affect other users messages, even if that message is in theory "the same".

This is probably too advanced for our needs but I'm writing down my thoughts to keep it in my head hehe.

## Soulless URL
I don't like when you click on things in a page and the URL doesn't reflect this, so refreshing the
page doesn't bring you back to where you were. Some sites solve this with sessions or local storage
but I prefer to keep this in the URL, mainly through the use of hash data (beyond the #), which 
also gives us history. 
I noticed that htmx doesn't allow this easily but it can change the URL based on your needs,
which does some weird hacking of local storage to store the dom, thus keeping history, I'm not
sure i like this because then pressing back brings you back to a saved local state instead of a
possibly updated remote state... either way, because the URLs used by htmx will return partials
for the use of htmx, we will need to make sure that our backend can return the full needed page
with the proper partial displayed for any URL that htmx "pushes" to the stack.
Using `django-url-framework` for this might not be optimal and we would probably be better off
using django's traditional views where we can more freely mess around with URL mapping to 
different functions.

