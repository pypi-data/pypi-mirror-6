from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from raptus.person.content.interfaces import IPerson


def person_factory(context):
    person = []
    seen = []
    for brain in context.portal_catalog(object_provides=IPerson.__identifier__):
        if brain.UID in seen:
            continue
        seen.append(brain.UID)
        person.append(SimpleTerm(brain.UID, brain.UID, brain.Title.decode('utf-8')))
    return SimpleVocabulary(person)