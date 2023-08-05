Introduction
============

raptus.contenttemplates allows to provide templates to automate specific
tasks. Templates are created by registering an adapter implementing the
ITemplate interface for the context the template should be available.

Actions
-------

All currently available actions are located at raptus.contenttemplates.actions,
new actions may be created by implementing the IAction interface.

ActionChains
------------

ActionChains are helpful if a list of actions have to be executed in the context
of a newly created object. Let's say one wants to create a document named test-document,
mark it private and give read access to the user jsmith and write access to jdoe.
The list returned by the template would look like this::

  [ActionChain((
      CreateContent('test-document', 'Document', {'title': 'Test Document'}),
      WorkflowTransition('hide'),
      AddLocalRole('jsmith', 'Reader'),
      AddLocalRole('jdoe', 'Editor')
   ))]
 
ActionChains respect the context returned by actions and use it to execute the
preceding action. Actions which create new content, return the newly created
object as context. The ActionChain then uses this context to execute the next
action.

FieldDataRetriever
------------------

FieldDataRetrievers allow to use a field of the provided form as an attribute
for an action. If one would like to have the aforementioned template use a form
providing the title for the document and have the id generated from that field.
The template would have to provide the name for the form and the action list 
could look like this::

  [ActionChain((
      CreateContent(FieldDataRetriever('title'), 'Document'),
      WorkflowTransition('hide'),
      AddLocalRole('jsmith', 'Reader'),
      AddLocalRole('jdoe', 'Editor')
   ))]
