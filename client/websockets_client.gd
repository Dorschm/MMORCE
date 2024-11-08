extends Node

const Packet = preload("res://packet.gd")

signal connected
signal data
signal disconnected
signal error

# Our WebSocketPeer instance
var socket = WebSocketPeer.new()

func _ready():
	var hostname = "cartandpod.com"
	var port = 80
	var websocket_url = "wss://%s:%d" % [hostname, port]
	var options = TLSOptions.client_unsafe()
	var err = socket.connect_to_url(websocket_url, options)

	if err != OK:
		print("Unable to connect")
		set_process(false)
		emit_signal("error")
	else:
		print("Connecting to WebSocket...")

func _process(delta):
	socket.poll()
	var state = socket.get_ready_state()
	if state == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			var packet = socket.get_packet()
			print("Packet: ", packet)
			data.emit(packet.get_string_from_utf8())
	elif state == WebSocketPeer.STATE_CLOSING:
		# Keep polling to achieve proper close.
		pass
	elif state == WebSocketPeer.STATE_CLOSED:
		var code = socket.get_close_code()
		var reason = socket.get_close_reason()
		print("WebSocket closed with code: %d, reason %s. Clean: %s" % [code, reason, code != -1])
		set_process(false) # Stop processing.
		emit_signal("disconnected")

func send_packet(packet: Packet) -> void:
	# Sends a packet to the server
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		_send_string(packet.tostring())
	else:
		print("WebSocket is not open. Cannot send packet.")

func _send_string(string: String) -> void:
	socket.send_text(string)
	print("Sent string ", string)

# Signal handlers for better logging
func _on_connected():
	print("WebSocket connected")
	emit_signal("connected")

func _on_disconnected():
	print("WebSocket disconnected")
	emit_signal("disconnected")

func _on_error():
	print("WebSocket error")
	emit_signal("error")

# Connect signals to handlers
socket.connect("connected", self, "_on_connected")
socket.connect("disconnected", self, "_on_disconnected")
socket.connect("error", self, "_on_error")
