# This script is keeping important functions for running automatic compositions in the future.

# THIS CODE DOES NOT WORK YET!!!


# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
# def update_compfile():

    # comp_events = DictReader(open("comp_events_template.csv"), skipinitialspace=True)
    # with open('composition_template.json', 'w') as compfile:

        # comp = {arg.pop('eventid'):{key:float(arg[key]) for key in arg} for arg in comp_events}
        # #logger.debug(f'COMP EVENTS F/ CSV: {comp}')
        # lastevent = len(comp)
        # comp[str(-lastevent)] = comp.pop(str(lastevent))
        # json.dump(comp, compfile, indent=4)

# ----------------------------------------------------------------------------------------------------------


# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
# def run_event(event):

    # global comp_events

    # logger.info(f'RUNNING EVENT {event}')
    # print(f'RUNNING EVENT {comp_events[0]} {event}')
    # logger.debug(f'DOING NOTHING FOR NOW')
# ----------------------------------------------------------------------------------------------------------

# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
    # try:
        # ce = DictReader(open("comp_events_template.csv"), skipinitialspace=True)
        # #print(ce)
        # open('composition_template.json', 'w')
    # except:
        # print("not successfulk")
    # if os.path.exists('composition_template.json'):
        # update_compfile()
        # with open('composition_template.json') as compfile:
            # composition = json.load(compfile)
            # comp_events = deque([int(x) for x in composition])
            # #logger.debug(f'LOADED COMPOSITION: {composition}')
            # reset = True
# ----------------------------------------------------------------------------------------------------------
    #print("here")
    
# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
        # if comp:
            # if comp_events[0] > 0:
                # current_event = int(comp_events[0])
            # elif comp_events[0] < 0:
                # current_event = -int(comp_events[0])
            # if last:
                # current_event = len(comp_events)+1
        # else:
            # current_event = 0

        # current_event -= 1
        # # --- PROMPT ---
        # x = session.prompt(f'({current_event}) VQH=> ', validator=validator, validate_while_typing=False)
# ----------------------------------------------------------------------------------------------------------

# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
            # if reset:
                # reset = False
            # if last:
                # comp_events.clear()
                # comp = False
            # try:
                # print(comp_events[0])
                # logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
            # except:
                # print(f'Score ended! type "reset" to reload')
                # continue
            # run_event(composition[str(comp_events[0])])

            # if comp_events[0] < 0:
                # print('END OF SCORE')
                # last = True
            # comp_events.rotate(-1)
        # elif x[0] == 'previous':
            # if not comp:
                # print(f'Score ended! type "reset" to reload')
                # continue
            # if not reset:
                # comp_events.rotate(2)
                # if comp_events[0] < 0:
                    # print('You are in the beginning! Cannot go back!')
                    # continue
                # logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
                # run_event(composition[str(comp_events[0])])
                # last = False
                # comp_events.rotate(-1)
            # else:
                # print('The score was reset! type "next" to begin')

        # elif x[0] == 'reset':
            # print(f'Resetting Score...')
            # comp_events = deque([int(x) for x in composition])
            # last = False
            # comp = True
        # elif x[0] == 'repeat':
            # if not comp:
                # print(f'Score ended! type "reset" to reload')
                # continue
            # if not reset:
                # comp_events.rotate(1)
                # logger.debug(f'EVENT : {comp_events[0]} {type(comp_events[0])}')
                # run_event(composition[str(comp_events[0])])
                # comp_events.rotate(-1)
            # else:
                # print('The score was reset! type "next" to begin')
        # elif x[0] == 'updatecomp':
            # update_compfile()
            # with open('composition.json') as compfile:
                # composition = json.load(compfile)
                # comp_events = deque([int(x) for x in composition])
                # logger.debug(f'UPDATED COMPOSITION: {composition}')
                # reset = True
# ----------------------------------------------------------------------------------------------------------

# Future work: creating, managing music compositions, rehearsal and performance ----------------------------
        # elif x[0] == 'set':
            # if len(x) != 2:
                # print('The "set" function expects one argument. ex:"=> set 2" goes to event 2. Type again.')
                # continue
            # e_id = int(x[1])
            # if e_id > len(comp_events):
                # print(f'Error. There is no event {e_id} in the score. Type again.')
                # continue
            # print(f'Setting Score. type "next" to go to event {x[1]}.')
            # comp_events = deque([int(x) for x in composition])
            # if e_id < 0:
                # e_id = -e_id
                # last=True
            # if e_id == 1:
                # reset=True
            # comp_events.rotate(-e_id+1)
            # comp = True
# ----------------------------------------------------------------------------------------------------------
