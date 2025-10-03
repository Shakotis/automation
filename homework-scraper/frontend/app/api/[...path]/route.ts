import { NextRequest, NextResponse } from 'next/server';

// This catches all /api/* routes and proxies them to Django backend
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyToDjango(request, resolvedParams.path);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyToDjango(request, resolvedParams.path);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyToDjango(request, resolvedParams.path);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyToDjango(request, resolvedParams.path);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyToDjango(request, resolvedParams.path);
}

async function proxyToDjango(request: NextRequest, path: string[]) {
  const DJANGO_API_URL = process.env.DJANGO_API_URL || 'http://127.0.0.1:8000';
  
  // Build the target URL
  const targetPath = path.join('/');
  const searchParams = request.nextUrl.searchParams.toString();
  const targetUrl = `${DJANGO_API_URL}/api/${targetPath}${searchParams ? `?${searchParams}` : ''}`;

  console.log(`[API Proxy] ${request.method} ${request.nextUrl.pathname} -> ${targetUrl}`);

  try {
    // Get request body if present
    let body = null;
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      try {
        body = await request.text();
      } catch (e) {
        // No body
      }
    }

    // Forward cookies from the request
    const cookies = request.headers.get('cookie') || '';
    console.log(`[API Proxy] Forwarding cookies: ${cookies}`);

    // Make request to Django
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: {
        'Content-Type': request.headers.get('content-type') || 'application/json',
        'Cookie': cookies,
        // Forward other important headers
        ...(request.headers.get('authorization') && {
          'Authorization': request.headers.get('authorization')!
        }),
      },
      body: body,
      credentials: 'include',
    });

    // Get response body
    const responseData = await response.text();
    
    // Create response with proper headers
    const nextResponse = new NextResponse(responseData, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'Content-Type': response.headers.get('content-type') || 'application/json',
      },
    });

    // Forward ALL Set-Cookie headers to maintain session
    const setCookieHeaders = response.headers.getSetCookie();
    if (setCookieHeaders && setCookieHeaders.length > 0) {
      console.log(`[API Proxy] Received Set-Cookie headers: ${setCookieHeaders.length}`);
      setCookieHeaders.forEach(cookie => {
        console.log(`[API Proxy] Original cookie: ${cookie}`);
        
        // Rewrite the cookie to work with localhost origin
        // Add SameSite=Lax for same-origin requests (since both frontend and proxy are on localhost:3000)
        let rewrittenCookie = cookie;
        
        // If cookie doesn't have SameSite attribute, add it
        if (!cookie.toLowerCase().includes('samesite=')) {
          rewrittenCookie = `${cookie}; SameSite=Lax`;
        }
        
        // If cookie doesn't have HttpOnly, add it for security (except for specific cookies)
        if (!cookie.toLowerCase().includes('httponly') && !cookie.includes('csrf')) {
          rewrittenCookie = `${rewrittenCookie}; HttpOnly`;
        }
        
        console.log(`[API Proxy] Rewritten cookie: ${rewrittenCookie}`);
        nextResponse.headers.append('Set-Cookie', rewrittenCookie);
      });
    }

    return nextResponse;

  } catch (error) {
    console.error('[API Proxy] Error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend server', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 502 }
    );
  }
}
