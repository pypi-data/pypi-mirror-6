###
StackMan
Client-side CoffeeScript
Colton J. Provias - cj@coltonprovias.com
Created: December 8, 2013

It may be ugly, but it works.

stackman.coffee: Automating stacks since December 2013
###


class TabManager
    # Self explanatory title: Check.

    constructor: (@element) ->
        # Set up our tab container with a tab area and a pane area.
        @tab_container = $ '<ul></ul>'
        @tab_container.attr 'id', 'tabs'
        @tab_container.addClass 'nav nav-tabs'
        @tab_container.appendTo @element
        @pane_container = $ '<div></div>'
        @pane_container.attr 'id', 'panes'
        @pane_container.addClass 'tab-content'
        @pane_container.appendTo @element

        # Set the counter to 0
        @tab_counter = 0

    clear: ->
        # Called whenever listing to reset everything
        @tab_container.html ''
        @pane_container.html ''
        @tab_counter = 0

    add_tab: (name, content) ->
        # Add a tab.  content should be a jQuery object.
        li = $ '<li></li>'
        li.addClass 'active' if @tab_counter is 0
        li.appendTo @tab_container

        link = $ '<a></a>'
        link.attr 'href', '#pane-' + @tab_counter
        link.addClass 'active' if @tab_counter is 0
        link.text name
        link.appendTo li
        link.click (event) ->
            event.preventDefault()
            target = $ event.target
            target.tab 'show'

        pane = $ '<div></div>'
        pane.addClass 'tab-pane'
        pane.addClass 'active' if @tab_counter is 0
        pane.attr 'id', 'pane-' + @tab_counter
        pane.appendTo @pane_container

        content.appendTo pane

        @tab_counter++


class TextField
    # Text input for the modals
    # Yes, I wrapped an input control.  So what?

    constructor: (@control_id, label_text, value="", @type="text") ->
        # Create the widget
        @widget = $ '<div>'
        @widget.addClass 'form-group'

        label = $ '<label>'
        label.attr 'for', @control_id
        label.html label_text
        label.appendTo @widget

        @control = $ '<input>'
        @control.attr 'type', @type
        @control.attr 'id', @control_id
        @control.addClass 'form-control'
        @control.val value
        @control.appendTo @widget

    get_value: -> @control.val()


class DropDown
    # Same thing as TextField except for a select element.

    constructor: (@control_id, label_text, options, value="") ->
        @widget = $ '<div>'
        @widget.addClass 'form-group'

        label = $ '<label>'
        label.attr 'for', @control_id
        label.html label_text
        label.appendTo @widget

        @control = $ '<select>'
        @control.attr 'id', @control_id
        @control.addClass 'form-control'

        for option in options
            opt = $ '<option>'
            opt.text option
            opt.val(option)
            opt.appendTo @control

        @control.val value
        @control.appendTo @widget

    get_value: -> @control.val()


class Checkbox
    # Checkbox: Filled in entirely with a number 2 penicl.

    constructor: (@control_id, label_text, is_selected=false) ->
        @widget = $ '<div>'
        @widget.addClass = 'checkbox'

        label = $ '<label>'
        label.text label_text
        label.appendTo @widget
        label.prepend ' '

        @control = $ '<input type="checkbox">'
        @control.attr 'id', @control_id
        @control.prop 'checked', is_selected
        @control.prependTo label

    get_value: -> @control.is ':checked'


class ModalBase
    # Give basic functionality to our modal

    constructor: ->
        # A lot of interface definition here.  *yawn*
        @modal = $ '<div>'
        @modal.addClass 'modal'
        @modal.attr 'id', 'modal'
        @modal.on 'hidden.bs.modal', $.proxy @destroy, this
        @modal.prependTo $ 'body'

        modal_dialog = $ '<div>'
        modal_dialog.addClass 'modal-dialog'
        modal_dialog.appendTo @modal

        modal_content = $ '<div>'
        modal_content.addClass 'modal-content'
        modal_content.appendTo modal_dialog

        modal_header = $ '<div>'
        modal_header.addClass 'modal-header'
        modal_header.appendTo modal_content

        button_exit = $ '<button>'
        button_exit.attr 'type', 'button'
        button_exit.attr 'data-dismiss', 'modal'
        button_exit.attr 'aria-hidden', 'true'
        button_exit.addClass 'close'
        button_exit.html '&times;'
        button_exit.appendTo modal_header

        @modal_title = $ '<div>'
        @modal_title.addClass 'modal-title'
        @modal_title.appendTo modal_header

        @modal_body = $ '<div>'
        @modal_body.addClass 'modal-body'
        @modal_body.appendTo modal_content

        modal_footer = $ '<div>'
        modal_footer.addClass 'modal-footer'
        modal_footer.appendTo modal_content

        @button_cancel = $ '<button>'
        @button_cancel.addClass 'btn btn-default'
        @button_cancel.attr 'data-dismiss', 'modal'
        @button_cancel.text 'Cancel'
        @button_cancel.appendTo modal_footer

        @button_save = $ '<button>'
        @button_save.addClass 'btn btn-primary'
        @button_save.text 'Save'
        @button_save.appendTo modal_footer

        @controls = []

        @modal.modal({backdrop: 'static'})
        @modal.modal('show')

    destroy: ->
        # Kill it with fire!
        if @modal isnt undefined
            @modal.remove()

    set_title: (title) ->
        @modal_title.html "<h4>#{title}</title>"

    add_p: (text) ->
        @modal_body.append $ "<p>#{text}</p>"

    add_control: (control) ->
        # Add a form control to the modal
        @controls.push control
        control.widget.appendTo @modal_body

    clear_controls: ->
        # Erase our cache of controls.  Useful for wizards.
        @controls = []

    show: -> @modal.modal 'show'

    hide: -> @modal.modal 'hide'


class AddStackModal extends ModalBase
    # Add a stack to StackMan

    constructor: ->
        super()
        @set_title 'Add Stack'
        @add_control new TextField 'stack-name', 'Stack Name'
        @button_save.click $.proxy @on_save, this
        @show()

    launch: (event) ->
        new AddStackModal

    on_save: (event) ->
        conn.submit '', 'addstack', @controls[0].get_value()
        @modal.modal('hide')


class StartAddItem extends ModalBase
    # Now a convoluted one: Adding Items

    constructor: (@stack) ->
        super()
        @stack_items = $(document).data 'stack_items'
        keys = Object.keys @stack_items
        keys.sort()
        @set_title 'Add Item'
        @add_control new DropDown 'item-type', 'Type to create', keys
        @button_save.text 'Next'
        @button_save.click $.proxy @on_first_save, this
        @show

    launch: (event) ->
        new StartAddItem

    on_first_save: (event) ->
        # Runs the first time you hit the primary button.  This generates the
        # next page of the modal
        @item_type = @controls[0].get_value()
        @clear_controls()
        @modal_body.html ''
        @button_save.text 'Add'
        @button_save.off 'click'
        @button_save.click $.proxy @on_second_save, this
        for field in @stack_items[@item_type]._args
            field_info = @stack_items[@item_type][field]
            switch field_info.type
                when 'str', 'int'
                    @add_control new TextField field, field_info.label, field_info.default
                when 'bool'
                    @add_control new Checkbox field, field_info.label, field_info.default

    on_second_save: (event) ->
        # The actual sending of the new item to the server
        args = {}
        for control in @controls
            args[control.control_id] = control.get_value()
        conn.submit @stack.id, 'additem', {class: @item_type, config: args}
        @modal.modal('hide')


class StackItem
    # We mirror the StackItems here just because we can...and because it helps.

    constructor: (@stack, payload) ->
        @status = payload._status
        @id = payload._id
        @class = payload._class
        @command = payload._command
        @config = payload
        @console_log = ''

    draw: ->
        # GUI Stuff!  Whooooo...zzzzzzZZZzzzZZzzz...
        @widget = $ '<div>'
        @widget.addClass 'panel'
        @widget.attr 'id', @stack.name + '--' + @config.name

        heading = $ "<div><strong>#{@config.name}</strong> </div>"
        heading.addClass 'panel-heading'
        heading.appendTo @widget

        @status_text = $ '<small>'
        @status_text.appendTo heading

        heading_buttons = $ '<div>'
        heading_buttons.addClass 'pull-right'
        heading_buttons.appendTo heading

        @start_button = $ '<button>Start</button>'
        @start_button.addClass 'btn btn-success btn-xs'
        @start_button.appendTo heading_buttons
        @start_button.click $.proxy @start, this
        heading_buttons.append ' '

        @stop_button = $ '<button>Stop</button>'
        @stop_button.addClass 'btn btn-danger btn-xs'
        @stop_button.appendTo heading_buttons
        @stop_button.click $.proxy @stop, this
        heading_buttons.append ' '

        @info_button = $ '<button>+ Show Info</button>'
        @info_button.addClass 'btn btn-info btn-xs'
        @info_button.appendTo heading_buttons
        @info_button.click $.proxy @toggle_body, this
        heading_buttons.append ' '

        @delete_button = $ '<button>Remove</button>'
        @delete_button.addClass 'btn btn-danger btn-xs'
        @delete_button.appendTo heading_buttons
        @delete_button.click $.proxy @remove, this
        heading_buttons.append ' '

        @move_buttons = $ '<div class="btn-group"></div>'
        @move_buttons.appendTo heading_buttons

        @move_up_button = $ '<button><span class="glyphicon glyphicon-chevron-up"></span></button>'
        @move_up_button.addClass 'btn btn-xs'
        @move_up_button.click $.proxy @move_up, this
        @move_up_button.appendTo @move_buttons

        @move_down_button =  $ '<button><span class="glyphicon glyphicon-chevron-down"></span></button>'
        @move_down_button.addClass 'btn btn-xs'
        @move_down_button.click $.proxy @move_down, this
        @move_down_button.appendTo @move_buttons

        @body = $ '<div>'
        @body.addClass 'panel-body'
        @body.appendTo @widget
        @body.hide()

        # Fun bit: Create the property table
        table = $ '<table><thead><tr><th width="200">Setting</th><th>Value</th></tr></thead></table>'
        table.addClass 'table table-condensed table-striped'
        table.appendTo @body
        tbody = $ '<tbody>'
        tbody.appendTo table
        for key in Object.keys @config
            tr = $ "<tr><td>#{key}</td><td>#{@config[key]}</td></tr>"
            tr.appendTo tbody

        @console_log = $ '<pre>'
        @console_log.css 'height', '400px'
        @console_log.css 'overflow', 'auto'
        @console_log.appendTo @body

        @footer = $ '<div>'
        @footer.addClass 'panel-footer'
        @footer.appendTo @widget
        @footer.hide()

        @update_widget()


    start: (event) ->
        # Start the item
        conn.submit @stack.id, 'start', @id

    stop: (event) ->
        # Stop the item
        conn.submit @stack.id, 'stop', @id

    remove: (event) ->
        # Kick the item out
        conn.submit @stack.id, 'removeitem', @id

    destroy: ->
        # Nuke the widget from orbit
        @widget.remove()

    move_up: (event) ->
        # Promote the item
        conn.submit @stack.id, 'moveup', @id
    
    move_down: (event) ->
        # Demote the item
        conn.submit @stack.id, 'movedown', @id

    add_log: (message, style=null) ->
        # Captain's Log.  Stardate: null.  My calendar still isn't working.
        if style isnt null
            message = "<span class='text-#{style}'>#{message}</span>"
        @console_log.append message
        @footer.html "<small>#{message}</small>"


    toggle_body: (event) ->
        # Now you see it, now you don't!  All with the press of a button.
        if @body.is(':visible')
            @info_button.text '+ Show Info'
            @body.hide()
        else
            @info_button.text '- Hide Info'
            @body.show()

    update_widget: (event) ->
        # Paint the widget and change the text.
        @widget.removeClass 'panel-success panel-danger panel-warning'
        @stop_button.hide()
        @start_button.hide()
        @footer.hide()
        switch @status
            when 'stopped'
                @widget.addClass 'panel-danger'
                @status_text.text 'Stopped'
                @start_button.show()
                @add_log '[StackMan] Stopped\n', 'primary'
            when 'ready'
                @widget.addClass 'panel-success'
                @status_text.text 'Ready'
                @stop_button.show()
                @add_log '[StackMan] Ready\n', 'primary'
            when 'stopping'
                @widget.addClass 'panel-warning'
                @status_text.text 'Stopping'
                @add_log '[StackMan] Stopping\n', 'primary'
            when 'running', 'starting'
                @widget.addClass 'panel-warning'
                @status_text.text 'Starting'
                @add_log '[StackMan] Starting\n', 'primary'
                @footer.show()

    process_command: (data) ->
        # Send the command to where it is appropriate
        switch data.command
            when 'status'
                @status = data.payload
                @update_widget()
            when 'stdout'
                @add_log data.payload
            when 'stderr'
                @add_log data.payload, 'danger'


class Stack
    # It holds stuff

    constructor: (@id, stack_data) ->
        # Load the items and all of the other crazy stuff
        @name = stack_data.name
        @items = []
        @item_container = $ '<div>'
        for item in stack_data.items
            @add_item item

    draw: ->
        # Did you know that I don't like how these draw functions are so long?
        # I originally wanted to cut them down, but then it gives more stuff to
        # fix.  At least it works.
        @widget = $ '<div>'

        toolbar = $ '<nav>'
        toolbar.addClass 'navbar navbar-default'
        toolbar.appendTo @widget

        toolbar_left = $ '<div>'
        toolbar_left.addClass 'navbar-form navbar-left'
        toolbar_left.appendTo toolbar

        toolbar_right = $ '<div>'
        toolbar_right.addClass 'navbar-form navbar-right'
        toolbar_right.appendTo toolbar

        @button_start = $ '<button>Start All</button>'
        @button_start.addClass 'btn btn-success navbar-btn btn-sm'
        @button_start.click $.proxy @start_all, this
        @button_start.appendTo toolbar_left

        toolbar_left.append ' '

        @button_stop = $ '<button>Stop All</button>'
        @button_stop.addClass 'btn btn-danger navbar-btn btn-sm'
        @button_stop.click $.proxy @stop_all, this
        @button_stop.appendTo toolbar_left

        toolbar_left.append ' '

        @button_delete = $ '<button>Delete Stack</button>'
        @button_delete.addClass 'btn btn-danger navbar-btn btn-sm'
        @button_delete.click $.proxy @remove, this
        @button_delete.appendTo toolbar_right
        toolbar_right.append ' '

        @button_rename = $ '<button>'
        
        @button_add = $ '<button>Add Item</button>'
        @button_add.addClass 'btn btn-primary navbar-btn btn-sm'
        @button_add.click $.proxy @on_add_click, this
        @button_add.appendTo toolbar_left

        @item_container.appendTo @widget

    start_all: (event) ->
        # Let the server do the work to start all of the items
        if @items.length > 0
            conn.submit @id, 'start', @items[@items.length-1].id

    stop_all: (event) ->
        # Stop everything!
        if @items.length > 0
            conn.submit @id, 'stop', @items[0].id

    index_by_id: (id) ->
        # Get an item by its ID.  Strangely, CoffeeScript doesn't stop a loop
        # even when return is issued.  Have to break it, too.
        for i in [0..(@items.length-1)]
            if @items[i].id is id
                return i
                break

    move_up: (id) ->
        # Move the actual panel for the item up.
        i = @index_by_id id
        k = i + 1
        start = @items[i]
        end = @items[k]
        start.widget.insertBefore end.widget
        [@items[i], @items[k]] = [@items[k], @items[i]]


    move_down: (id) ->
        # Push the item down a notch.
        i = @index_by_id id
        k = i - 1
        start = @items[i]
        end = @items[k]
        start.widget.insertAfter end.widget
        [@items[i], @items[k]] = [@items[k], @items[i]]

    remove: (event) ->
        # Call for this stack's removal.  It returns a list command, which
        # just refreshes everything.
        conn.submit @id, 'removestack', []

    on_add_click: (event) ->
        # Let's add a new item and slow your computer down more!
        new StartAddItem this

    add_item: (payload) ->
        # Add the item to the stack and add the widget to the DOM
        item = new StackItem this, payload
        @items.push item
        item.draw()
        item.widget.prependTo @item_container

    remove_item: (sender) ->
        # Pull the item out of the stack and call for it to destroy its widget
        for i in [0..(@items.length-1)]
            if @items[i].id is sender
                @items[i].destroy()
                @items.splice(i, 1)
                break

    process_command: (data) ->
        # It's just like being in the mailroom, except this is much more
        # efficient.
        if data.command is 'additem'
            @add_item data.payload
        else if data.command is 'removeitem'
            @remove_item data.sender
        else if data.command is 'moveup'
            @move_up data.sender
        else if data.command is 'movedown'
            @move_down data.sender
        for item in @items
            if item.id is data.sender
                item.process_command data


class StackManager
    # Just a way to hold all of our stacks so I don't put it in something else
    # like a socket handler or something stupid like that.

    constructor: ->
        @stacks = []

    stack_sorter: (a, b) ->
        # Provide a way to sort the stacks
        a = a[1].config.name.toLowerCase()
        b = b[1].config.name.toLowerCase()
        if a < b then -1 else (if a > b then 1 else 0)

    load_stacks: (payload) ->
        # Load the stacks in and display them
        tabs.clear()
        stacks = []
        for key, value of payload.stacks
            stacks.push [key, value]
        stacks.sort @stack_sorter
        for s in stacks
            @add_stack s[0], s[1]

    add_stack: (name, data) ->
        # Add a stack
        stack = new Stack name, data
        @stacks.push stack
        stack.draw()
        tabs.add_tab stack.name, stack.widget

    process_command: (data) ->
        # Route the command to the right stack or destination
        if data.command is 'addstack'
            @add_stack data.stack, data.payload
        else
            for stack in @stacks
                if stack.id is data.stack
                    stack.process_command data


class Connection
    # Handle the websocket

    constructor: ->
        # Set it up and configure it
        @socket = new WebSocket 'ws://' + location.host + '/socket'
        @socket.onmessage = $.proxy @process_message, this 

    process_message: (event) ->
        # Handle incoming messages.  If it's a list command, redo everything.
        data = JSON.parse event.data
        console.log data
        if data.command is 'list'
            $(document).data 'stack_items', data.payload.items
            stack_manager.load_stacks data.payload
        else
            stack_manager.process_command data

    submit: (stack, command, arg) ->
        # Send a message
        message =
            stack: stack
            command: command
            arg: arg
        message = JSON.stringify message
        @socket.send message


# Now to run things.  First set up a new StackManager
stack_manager = new StackManager

# Set up our Add Stack button.
button_add_stack = $ '#btn-add'
button_add_stack.click (event) ->
    new AddStackModal

# Initialize the tabs
tabs = new TabManager $ '#stacks'

# Set up the connection, call for a list, and away we go!
conn = new Connection
conn.socket.onopen = (event) ->
    conn.submit '', 'list', []
