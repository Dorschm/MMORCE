extends Node

const Packet = preload("res://packet.gd")

signal connected
signal data
signal disconnected
signal error

# Our WebSocketPeer instance
var socket = WebSocketPeer.new()

func _ready():
	var hostname = "cartandpod.com"  # Replace with your actual domain
	var port = 80  # Use port 80 for HTTP, as Cloudflare handles SSL/TLS
	var websocket_url = "ws://%s:%d" % [hostname, port]
	var err = socket.connect_to_url(websocket_url)

	if err != OK:
		print("Unable to connect, error code: ", err)
		set_process(false)
		emit_signal("error")
	else:
		print("Connecting to WebSocket...")

func _process(delta):
	socket.poll()
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		print("WebSocket is open")
		while socket.get_available_packet_count():
			var packet = socket.get_packet()
			print("Packet: ", packet)
			data.emit(packet.get_string_from_utf8())
	elif state == WebSocketPeer.STATE_CONNECTING:
		print("WebSocket is connecting...")
	elif state == WebSocketPeer.STATE_CLOSING:
		print("WebSocket is closing...")
	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.

func send_packet(packet: Packet) -> void:
	# Sends a packet to the server
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		_send_string(packet.tostring())
	else:
		print("WebSocket is not open. Cannot send data.")

func _send_string(string: String) -> void:
	socket.send_text(string)
	print("Sent string ", string)

# Additional debug function to check connection status
func check_connection_status():
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_CONNECTING:
		print("WebSocket is still connecting...")
	elif state == WebSocketPeer.STATE_OPEN:
		print("WebSocket is open")
	elif state == WebSocketPeer.STATE_CLOSING:
		print("WebSocket is closing...")
	elif state == WebSocketPeer.STATE_CLOSED:
		print("WebSocket is closed")

# Call this function periodically to check the connection status
func _process2(delta):
	socket.poll()
	check_connection_status()
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var packet = socket.get_packet()
			print("Packet: ", packet)
			data.emit(packet.get_string_from_utf8())
	elif socket.get_ready_state() == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.
