from src.commands import command_on_message
from src.tools.state_machines import Machine, Action, State

class machine_dual(command_on_message):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    # Here is a demonstration of a machine with two states, with no data.
    async def action(self, message):
        # First, let's define our two states. Since our actions haven't been defined yet, we'll add them later.
        first_state = State.from_dict(
                embed_dict={
                    'title': 'First State',
                    'description': "I'm the first state in this machine!"
                }
        )
        second_state = State.from_dict(
            embed_dict={
                    'title': 'Second State',
                    'description': "I'm the second state in this machine!"
                },
        )
        
        # Now, let's define our actions. Due to ease of use, we'll use the .new decorator
        @Action.new(label='Go Forward!')
        async def go_to_first_state(machine: Machine, interaction):
            await machine.update_state(first_state, interaction)

        @Action.new(label='Go Back!')
        async def go_to_second_state(machine: Machine, interaction):
            await machine.update_state(second_state, interaction)

        # Now let's add actions to our states.

        first_state.add_action(go_to_second_state)
        second_state.add_action(go_to_first_state)
        
        await Machine.create(first_state, message, timeout=10) # And finally, create our machine!
        return None

    @staticmethod
    def helptxt():
        return '$machine_dual \nGenerates a sample dual state machine'

class machine_counter(command_on_message):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    # Here is a demonstration of a machine using its data! This machine will count up by 1 everytime a button is pressed.
    async def action(self, message):
        # Let's first create our base state. We want this to be formatted as a template since other states will derive from this.
        base_state = State.make_template(
            title='Counter',
            description='The counter is currently at {number}',
            count='#count' # Assigning a key to '#key' will tell State.format that this key should not be assigned to a string. In our case, we want count to be an int.
        )

        @Action.new(label='+1')
        async def take_action(machine: Machine, interaction):
            # Since this machine revolves around counting by increments of 1, let's define our new number.
            new_number = machine['count'] + 1 
            # Note that the machine object CAN be treated like a dictionary; machine['count'] is the same as machine.data['count']

            # Now lets create our state object, using from_state and format.
            new_state = State.from_state(base_state).format(number=str(new_number), count=new_number)
            # Since format won't accept strings
            new_state['count'] = new_number
            # And now we update the machine!
            await machine.update_state(new_state, interaction)

        # Now let's add the action and create the initial state
        base_state.add_action(take_action)
        initial_state = State.from_state(base_state).format(number='0', count=0)
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
        # Let's first define our base state.
        base_state = State.make_template(
            title='{order} State', # {order} refers to either 'First' or 'Second'. {lower_order} is a lowercase version of this.
            description='You are in the {lower_order} state! This machine has changed states {times}!', # Times refers to the number of times this machine has changed states.
            count='#count'
        )

        # Now let's define our actions
        @Action.new(label='Go Forward!')
        async def go_to_first_state(machine: Machine, interaction):
            # First calculating our new number
            current_count = machine['count'] + 1
            # Since '1 times' is incorrect, let's add a small checker that can change it to '1 time'.
            correct_string = str(current_count) + ' times!' if current_count != 1 else str(current_count) + ' time!'

            # And now let's create our new state.
            new_state = State.from_state(base_state).format(
                order='First', 
                lower_order='first', 
                times=correct_string,
                count = current_count
            ).add_action(go_to_second_state) # We want to add the second action since no actions are included in the base state.
            # Now let's update the machine
            await machine.update_state(new_state, interaction)

        # Now let's make our second action. It will be almost identical so no additional comments is needed.
        async def go_to_second_state(machine: Machine, interaction):
            current_count = machine['count'] + 1
            correct_string = str(current_count) + ' times!' if current_count != 1 else str(current_count) + ' time!'

            new_state = State.from_state(base_state).format(
                order='Second', 
                lower_order='second', 
                times=correct_string,
                count = current_count
            ).add_action(go_to_first_state)

            await machine.update_state(new_state, interaction)

        # Now let's create our machine! Note that our initial state will be the first state with a count of 0
        initial_state = State.from_state(base_state).format(
                order='First', 
                lower_order='first', 
                times='0 times',
                count=0
            ).add_action(go_to_second_state)
        # And then make the machine
        await Machine.create(initial_state, message, timeout=10)
        return None
