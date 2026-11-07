export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  try {
    const response = await fetch(
      `${backendUrl}/api/search?${searchParams.toString()}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        next: { revalidate: 60 },
      }
    )

    if (!response.ok) {
      return Response.json(
        { error: `Backend error: ${response.status}`, results: [], total: 0, query: searchParams.get('q') || '', cached: false, sources_queried: [] },
        { status: response.status }
      )
    }

    const data = await response.json()
    return Response.json(data)
  } catch (error) {
    console.error('Search proxy error:', error)
    return Response.json(
      {
        error: 'Failed to connect to backend',
        results: [],
        total: 0,
        query: searchParams.get('q') || '',
        cached: false,
        sources_queried: [],
      },
      { status: 503 }
    )
  }
}
