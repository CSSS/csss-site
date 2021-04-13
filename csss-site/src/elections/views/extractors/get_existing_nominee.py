from elections.models import Nominee


def get_exist_nominee(nominee_id, election_id):
    """
    Gets the Nominee object that maps to the specified ID

    Keyword Argument:
    nominee_id -- the ID of the Nominee object to obtain
    election_id -- the ID of the election that the nominee is running in

    Return
    Nominee -- the nominee object or None if no matching nominees found
    """
    nominees = Nominee.objects.all().filter(election_id=election_id, id=nominee_id)
    if len(nominees) != 1:
        return None
    return nominees[0]