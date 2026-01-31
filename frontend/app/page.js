export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Kalm</h1>
          <p className="text-white/80 text-lg">
            Your 24/7 recovery companion
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Get Support Now
          </h2>
          <p className="text-gray-600 mb-6">
            Message our Telegram bot anytime and receive a supportive voice note within seconds.
          </p>

          <a
            href="https://t.me/kalm_ai_bot"
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full py-4 px-4 bg-[#0088cc] text-white font-semibold rounded-lg hover:bg-[#0077b5] transition-colors text-center"
          >
            <span className="flex items-center justify-center gap-2">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
              Chat with Kalm on Telegram
            </span>
          </a>

          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-sm text-gray-500">
              Just say how you're feeling and receive an AI-generated voice message of support.
            </p>
          </div>
        </div>

        <p className="text-center text-white/60 text-sm mt-6">
          You are not alone. Help is always available.
        </p>
      </div>
    </main>
  )
}
