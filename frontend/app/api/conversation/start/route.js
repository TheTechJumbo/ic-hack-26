export async function POST() {
  const agentId = process.env.ELEVENLABS_AGENT_ID
  const apiKey = process.env.ELEVENLABS_API_KEY

  if (!agentId || !apiKey) {
    return Response.json(
      { error: 'ElevenLabs not configured' },
      { status: 500 }
    )
  }

  try {
    const response = await fetch(
      `https://api.elevenlabs.io/v1/convai/conversation/get_signed_url?agent_id=${agentId}`,
      {
        method: 'GET',
        headers: {
          'xi-api-key': apiKey,
        },
      }
    )

    if (!response.ok) {
      const error = await response.text()
      return Response.json(
        { error: `ElevenLabs API error: ${error}` },
        { status: response.status }
      )
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    return Response.json(
      { error: `Request failed: ${error.message}` },
      { status: 500 }
    )
  }
}
