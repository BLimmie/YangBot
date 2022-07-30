from src.commands import command_on_message
from src.tools.state_machines import Machine, Action, State

class machine_dual(command_on_message):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    # Here is a demonstration of a machine with two states, with no data.
    async def action(self, message):
        # Let's define the callbacks for each action, along with the state they'll be put into.
        async def first_state_action(machine: Machine, interaction):
            # First we need to specify the new state object
            new_state = State.from_dict(
                embed_dict={ # When interacting with the first button, we want to move into the second state.
                    'title': 'Second State',
                    'description': "I'm the second state in this machine!"
                },
                actions=[
                    Action(machine, callback=second_state_action, label='Go back!') # This may seem a bit confusing, but what we're doing is creating the action for the second state, and assigning second_state_action to its callback.
                ]
            )
            await machine.update_state(new_state, interaction) # And we finally update the machine!

        # Similarly with the second state
        async def second_state_action(machine: Machine, interaction):
            # First create a new state
            new_state = State.from_dict(
                embed_dict={
                    'title': 'First State',
                    'description': "I'm the first state in this machine!"
                },
                actions=[
                    Action(machine, callback=first_state_action, label='Go forward!') # Like before, we set the first state's action to be the first_action.
                ]
            )
            await machine.update_state(new_state, interaction) # And then update the machine!

        # Now let's create the initial state
        initial_state = State.from_dict( 
            embed_dict={
                'title': 'First State',
                'description': "I'm the very first state in this machine!"
            }, 
            actions=[
                Action(callback=first_state_action, label="Go forward!") # Since we haven't made our machine yet, it doesn't need to be passed. machine.create() will handle that.
            ]
        )
        await Machine.create(initial_state, message, timeout=10) # And finally, create our machine!
        return None

    @staticmethod
    def helptxt():
        return '$machine_dual \nGenerates a sample dual state machine'

class machine_counter(command_on_message):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    # Here is a demonstration of a machine using its data! This machine will count up by 1 everytime a button is pressed.
    async def action(self, message):
        # Let's first define the callback.
        async def take_action(machine: Machine, interaction):
            # Since this machine revolves around counting by increments of 1, let's define our new number.
            new_number = machine['count'] + 1 
            # Note that the machine object CAN be treated like a dictionary; machine['count'] is the same as machine.data['count']

            # Now lets create our state object. Since the new state will be almost identical to the previous one, we can simply copy it directly.
            new_state = State.from_state(machine.state)
            # We'll now need to edit our new state before passing it. Recall that dotted access will refer to the embed, while keyed access will refer to data.
            new_state.description = 'The counter is currently at ' + str(new_number)
            new_state['count'] = new_number
            # And now we update the machine!
            await machine.update_state(new_state, interaction)

        # Now let's create the initial state
        initial_state = State.from_dict( 
                embed_dict={
                    'title': 'Counter',
                    'description': 'The counter is currently at 0' # Count starts at 0!
                },
                actions=[
                    Action(callback=take_action, label='+1') # As before, we don't have a machine yet, so we don't need to specify it!
                ],
                data={
                    'count': 0
                }
        )
        await Machine.create(initial_state, message, timeout=10) # And finally, create our machine!
        return None

    @staticmethod
    def helptxt():
        return '$machine_counter \nCreates a machine capable of counting in increments of 1.'

class machine_dual_counter(command_on_message):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    # Here is a combined demonstration of the two examples above; a machine with two states that also uses a counter.
    async def action(self, message):
        # Let's first define our two coroutines for action
        async def first_action(machine: Machine, interaction):
            # First calculating our new number
            current_count = machine['count'] + 1
            # Since '1 times' is incorrect, let's add a small checker that can change it to '1 time'.
            correct_string = str(current_count) + ' times!' if current_count != 1 else str(current_count) + ' time!'

            # And now let's create our new state. Note that our action moves into the second state.
            new_state = State.from_dict(
                embed_info = {
                    'title': 'Second State',
                    'description': 'You are in the second state! This machine has changed states ' + correct_string
                },
                actions = [
                    Action(machine, callback=second_action, label='Go back!')
                ],
                data = {
                    'count': current_count
                }
            )
            # Now let's update the machine
            await machine.update_state(new_state, interaction)

        # Now let's make our second action. It will be almost identical so no additional comments is needed.
        async def second_action(machine: Machine, interaction):
            current_count = machine['count'] + 1
            correct_string = str(current_count) + ' times!' if current_count != 1 else str(current_count) + ' time!'

            new_state = State.from_dict(
                embed_info = {
                    'title': 'First State',
                    'description': 'You are in the first state! This machine has changed states ' + correct_string
                },
                actions = [
                    Action(machine, callback=first_action, label='Go forward!')
                ],
                data = {
                    'count': current_count
                }
            )
            await machine.update_state(new_state, interaction)

        # Now let's create our machine! First we need our initial state
        initial_state = State.from_dict(
            embed_info = {
                'title': 'First State',
                'description': 'You are in the first state! This machine has changed states 0 times!'
            },
            actions = [
                Action(callback=first_action, label='Go forward!')
            ],
            data = {
                'count': 0
            }
        )
        # And then make the machine
        await Machine.create(initial_state, message, timeout=10)
        return None
