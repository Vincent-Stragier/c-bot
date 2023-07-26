/* eslint-env jquery */
$(document).ready(function () {
  // Number of messages in the chat
  let NumberOfMessages = 0
  // Lock to prevent multiple messages from being sent at the same time
  let Lock = false
  // Current bot message id
  let CurrentBotMessageID = 0

  function GetNumberOfMessages () {
    // Returns the number of messages in the chat
    return NumberOfMessages
  }

  function CurrentDatetimeString () {
    // Returns a string with the current date and time
    const Current = new Date()
    return (
      Current.getFullYear() +
      '-' +
      (Current.getMonth() + 1) +
      '-' +
      Current.getDate() +
      ' ' +
      Current.getHours() +
      ':' +
      Current.getMinutes() +
      ':' +
      Current.getSeconds()
    )
  }

  function MessageAddedEvent (LastMessageID, UpdateID = true) {
    // To be added in each function that adds a message...
    if (UpdateID === true) {
      NumberOfMessages += 1
    }

    let Messages = NumberOfMessages.toString() + ' message'
    if (NumberOfMessages > 1) {
      Messages += 's'
    }

    document.getElementById('number_of_messages').innerHTML = Messages
    document
      .getElementById('user_input')
      .scrollIntoView({ block: 'start', behavior: 'smooth' })

    document
      .getElementById(LastMessageID)
      .scrollIntoView({ block: 'start', behavior: 'smooth' })
  }

  function AddMessage (Message, LiClass, SpanClass, Name, Datetime) {
    // Add user message
    const MessageID = 'message_' + GetNumberOfMessages()

    let MessageHeader = ''

    // if (message === "") {
    //   // Add a "typing" animation
    //   message = '<div class="typing"></div>';
    // }

    if (LiClass === 'me') {
      MessageHeader =
        '<h3>' +
        Datetime +
        '  ' +
        '</h3><h2>' +
        Name +
        '  </h2><span class="' +
        SpanClass +
        '"></span>'
    } else if (LiClass === 'you') {
      MessageHeader =
        '<span class="' +
        SpanClass +
        '"></span>' +
        '  <h2>' +
        Name +
        '</h2>' +
        '  <h3>' +
        Datetime +
        '</h3>'
    }

    console.log(MessageID)
    $('#chat').append(
      '<li class="' +
      LiClass +
      '"><div class="header">' +
      MessageHeader +
      '</div>' +
      // '<div class="triangle"></div>' +
      '<div class=message id="' +
      MessageID +
      '">' +
      Message +
      '</div></li>'
    )
    MessageAddedEvent(MessageID)
  }

  function UpdateMessage (Message, MessageID) {
    document.getElementById(MessageID).innerHTML += Message
    MessageAddedEvent(MessageID, false)
  }

  /* eslint-disable no-undef */
  const socket = io.connect()
  /* eslint-enable no-undef */

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

    /* eslint-disable no-undef */
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
    /* eslint-enable no-undef */

    audio.loop = false
    audio.play()
  })

  socket.on('message', function (msg) {
    console.log('Received message :: ' + msg.start + ' ' + msg.end + ' ' + msg.content)

    // Add bot message
    const BotName = 'C-Bot'

    if (msg.start === true) {
      console.log('start bot message')
      AddMessage(
        msg.content,
        'you', // This is a bot message
        'status green',
        BotName,
        CurrentDatetimeString()
      )

      // Update current bot message id (-1, since the message id starts at 0)
      CurrentBotMessageID = GetNumberOfMessages() - 1
    } else {
      UpdateMessage(msg.content, 'message_' + CurrentBotMessageID)
    }

    if (msg.end === true) {
      Lock = false
    }
  })

  function GetInteractiveAgentResponse (UserName = 'Vincent') {
    const UserText = $('#user_input_text').val()
    let UserDatetime = 'HH:mm, Date (today, yesterday, date)'
    // Set Lock to prevent multiple messages from being sent at the same time
    Lock = true

    // Reset user input text area
    $('#user_input_text').val('')

    // If the user input text area is empty, do nothing
    if (UserText === '' || UserText === '\n') {
      Lock = false
      return
    }

    // Get current date and time
    UserDatetime = CurrentDatetimeString()

    // Add me (user) message
    AddMessage(UserText, 'me', 'status blue', UserName, UserDatetime)

    // Send user message via websocket
    socket.emit('message', UserText)
  }

  $('#user_input_text').keypress(function (key) {
    // If the enter key is pressed in the user input text area,
    // request a response from the interactive agent
    if (key.which === 13 && Lock === false) {
      GetInteractiveAgentResponse()
    }
    // Remove \n from user input text area
    if (key.which === 13) {
      key.preventDefault()
    }
  })

  $('#user_input_button').click(function () {
    // If the user clicks on the send button,
    // request a response from the interactive agent
    if (Lock === true) {
      return
    }
    GetInteractiveAgentResponse()
  })

  $('#chat').change(function () {
    console.log('chat changed')
  })
})
