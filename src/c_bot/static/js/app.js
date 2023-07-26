$(document).ready(function () {
  // Number of messages in the chat
  let number_of_messages = 0
  // Lock to prevent multiple messages from being sent at the same time
  let lock = false
  // Current bot message id
  let current_bot_message_id = 0

  function get_number_of_messages () {
    // Returns the number of messages in the chat
    return number_of_messages
  }

  function current_datetime_string () {
    // Returns a string with the current date and time
    const current = new Date()
    return (
      current.getFullYear() +
      '-' +
      (current.getMonth() + 1) +
      '-' +
      current.getDate() +
      ' ' +
      current.getHours() +
      ':' +
      current.getMinutes() +
      ':' +
      current.getSeconds()
    )
  }

  function message_added_event (last_message_id, update_id = true) {
    // To be added in each function that adds a message...
    if (update_id == true) {
      number_of_messages += 1
    }

    messages = number_of_messages.toString() + ' message'
    if (number_of_messages > 1) {
      messages += 's'
    }

    document.getElementById('number_of_messages').innerHTML = messages
    document
      .getElementById('user_input')
      .scrollIntoView({ block: 'start', behavior: 'smooth' })

    document
      .getElementById(last_message_id)
      .scrollIntoView({ block: 'start', behavior: 'smooth' })
  }

  function add_message (message, li_class, span_class, name, datetime) {
    // Add user message
    const message_id = 'message_' + get_number_of_messages()

    let message_entete = ''

    // if (message == "") {
    //   // Add a "typing" animation
    //   message = '<div class="typing"></div>';
    // }

    if (li_class == 'me') {
      message_entete =
        '<h3>' +
        datetime +
        '  ' +
        '</h3><h2>' +
        name +
        '  </h2><span class="' +
        span_class +
        '"></span>'
    } else if (li_class == 'you') {
      message_entete =
        '<span class="' +
        span_class +
        '"></span>' +
        '  <h2>' +
        name +
        '</h2>' +
        '  <h3>' +
        datetime +
        '</h3>'
    }

    console.log(message_id)
    $('#chat').append(
      '<li class="' +
      li_class +
      '"><div class="entete">' +
      message_entete +
      '</div>' +
      // '<div class="triangle"></div>' +
      '<div class=message id="' +
      message_id +
      '">' +
      message +
      '</div></li>'
    )
    message_added_event(message_id)
  }

  function update_message (message, message_id) {
    document.getElementById(message_id).innerHTML += message
    message_added_event(message_id, false)
  }

  const socket = io.connect()

  socket.on('speech', function (msg) {
    console.log(
      "Received speech command :: text: '" +
      msg.text +
      "', voice: " +
      msg.voice +
      ', rate: ' +
      msg.rate +
      ', volume: ' +
      msg.volume
    )

    const audio = new Audio(
      '/a?text=' +
      msg.text +
      '&voice=' +
      msg.voice +
      '&rate=' +
      msg.rate +
      '&volume=' +
      msg.volume
    )
    audio.loop = false
    audio.play()
  })

  socket.on('message', function (msg) {
    // Add interactive agent message
    const bot_name = 'Agent interactif'

    if (msg.start == true) {
      add_message(
        '',
        'you',
        'status green',
        bot_name,
        current_datetime_string()
      )
      // Update current bot message id (-1, since the message id starts at 0)
      current_bot_message_id = get_number_of_messages() - 1
    } else if (msg.end == false && msg.start == false) {
      update_message(msg.content, 'message_' + current_bot_message_id)
    } else if (msg.end == true) {
      lock = false
    }
  })

  function get_interactive_agent_response (user_name = 'Vincent') {
    const user_text = $('#user_input_text').val()
    let user_datetime = 'HH:mm, Date (today, yesterday, date)'
    // Set lock to prevent multiple messages from being sent at the same time
    lock = true

    // Reset user input text area
    $('#user_input_text').val('')

    // If the user input text area is empty, do nothing
    if (user_text == '' || user_text == '\n') {
      lock = false
      return
    }

    // Get current date and time
    user_datetime = current_datetime_string()

    // Add me (user) message
    add_message(user_text, 'me', 'status blue', user_name, user_datetime)

    // Send user message via websocket
    socket.emit('message', user_text)
  }

  $('#user_input_text').keypress(function (key) {
    // If the enter key is pressed in the user input text area,
    // request a response from the interactive agent
    if (key.which == 13 && lock == false) {
      get_interactive_agent_response()
    }
    // Remove \n from user input text area
    if (key.which == 13) {
      key.preventDefault()
    }
  })

  $('#user_input_button').click(function () {
    // If the user clicks on the send button,
    // request a response from the interactive agent
    if (lock == true) {
      return
    }
    get_interactive_agent_response()
  })

  $('#chat').change(function () {
    console.log('chat changed')
  })
})
