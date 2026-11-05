<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TradeVortex School of Trading | Institutional SMC Mentorship by Mr. Yusuf</title>
    
    <!-- SEO Meta Tags -->
    <meta name="description" content="TradeVortex School of Trading by Mr. Yusuf. Master Smart Money Concepts (SMC), live Google Meet mentorship, algorithmic trading setups, and institutional analytics terminal.">
    <meta name="keywords" content="trading free class, AI trading tools, Smart Money Concepts, SMC trading course, Google Meet trading class, stock market mentorship, TradeVortex, algorithmic trading India, Nifty options analysis">
    <meta name="author" content="Mr. Yusuf">

    <!-- Open Graph Social Tags -->
    <meta property="og:title" content="TradeVortex School of Trading | Institutional SMC Mentorship">
    <meta property="og:description" content="Master Smart Money Concepts and get free AI trading tools and live analytics terminal.">
    <meta property="og:type" content="website">

    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkBg: '#0B0F19',
                        cardBg: '#131C2E',
                        accentGold: '#F59E0B',
                        accentCyan: '#06B6D4',
                        accentEmerald: '#10B981'
                    },
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'sans-serif']
                    }
                }
            }
        }
    </script>

    <style>
        .active-nav-link {
            color: #F59E0B !important;
            border-bottom: 2px solid #F59E0B;
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0B0F19;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
        .glow-gold {
            box-shadow: 0 0 25px -5px rgba(245, 158, 11, 0.2);
        }
        .glow-emerald {
            box-shadow: 0 0 25px -5px rgba(16, 185, 129, 0.25);
        }
    </style>
</head>
<body class="bg-darkBg text-slate-100 font-sans antialiased selection:bg-accentGold selection:text-black min-h-screen flex flex-col justify-between">

    <!-- TOP ANNOUNCEMENT BANNER WITH LIVE COUNTDOWN -->
    <div class="bg-gradient-to-r from-amber-600/30 via-amber-500/20 to-amber-600/30 border-b border-amber-500/30 py-2.5 px-4 text-center text-xs font-medium text-amber-200 flex flex-wrap justify-center items-center gap-2">
        <span class="inline-flex items-center gap-2">
            <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
            </span>
            <strong class="font-bold">⚡ Limited Free Access Slots Today:</strong> Institutional Terminal Pass available via Partner Onboarding.
        </span>
        <span id="countdown" class="bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded font-mono font-bold border border-amber-500/30">03h : 45m : 12s</span>
        <a href="https://a.aonelink.in/ANGOne/tNCsDi3" target="_blank" class="underline hover:text-white font-semibold ml-1">Claim Access Now →</a>
    </div>

    <!-- MAIN NAVIGATION BAR -->
    <nav class="sticky top-0 z-50 bg-darkBg/95 backdrop-blur-md border-b border-slate-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-20">
                <div class="flex items-center space-x-3 cursor-pointer" onclick="switchTab('home')">
                    <span class="text-2xl font-black tracking-tight text-white">Trade<span class="text-accentGold">Vortex</span></span>
                    <span class="hidden sm:inline-block text-xs font-semibold bg-slate-800/80 text-slate-300 px-3 py-1 rounded-full border border-slate-700">Institutional Academy</span>
                </div>

                <div class="hidden md:flex items-center space-x-8 text-sm font-semibold text-slate-400">
                    <button onclick="switchTab('home')" id="nav-home" class="nav-btn hover:text-white transition-colors py-2 active-nav-link">Home</button>
                    <button onclick="switchTab('proof')" id="nav-proof" class="nav-btn hover:text-white transition-colors py-2">Live Meet Proofs</button>
                    <button onclick="switchTab('curriculum')" id="nav-curriculum" class="nav-btn hover:text-white transition-colors py-2">Curriculum</button>
                    <button onclick="switchTab('contact')" id="nav-contact" class="nav-btn hover:text-white transition-colors py-2">Support Desk</button>
                </div>

                <div class="flex items-center gap-3">
                    <button onclick="openLeadModal('Open Demat Account & Claim Free Terminal')" class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs sm:text-sm px-5 py-2.5 rounded-xl transition-all shadow-lg shadow-emerald-950/50 flex items-center gap-2">
                        <span>Open Demat Account</span>
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"/></svg>
                    </button>
                </div>
            </div>

            <div class="flex md:hidden border-t border-slate-800/60 py-2 justify-around text-xs font-semibold text-slate-400 overflow-x-auto">
                <button onclick="switchTab('home')" id="mob-nav-home" class="nav-mob-btn px-3 py-1.5 active-nav-link">Home</button>
                <button onclick="switchTab('proof')" id="mob-nav-proof" class="nav-mob-btn px-3 py-1.5">Live Meets</button>
                <button onclick="switchTab('curriculum')" id="mob-nav-curriculum" class="nav-mob-btn px-3 py-1.5">Curriculum</button>
                <button onclick="switchTab('contact')" id="mob-nav-contact" class="nav-mob-btn px-3 py-1.5">Support</button>
            </div>
        </div>
    </nav>

    <!-- CONTENT WRAPPER -->
    <main id="main-content" class="flex-grow">

        <!-- PAGE 1: HOME -->
        <section id="page-home" class="page-section">
            <header class="relative overflow-hidden py-16 sm:py-24 border-b border-slate-800/80 bg-gradient-to-b from-darkBg via-slate-900/50 to-darkBg">
                <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
                    <span class="inline-flex items-center gap-2 bg-amber-500/10 text-accentGold border border-amber-500/20 text-xs font-bold px-4 py-1.5 rounded-full uppercase tracking-wider mb-6">
                        🔥 500+ Active Institutional Traders Joined
                    </span>
                    <h1 class="text-4xl sm:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight">
                        Institutional Grade Execution & <span class="text-transparent bg-clip-text bg-gradient-to-r from-accentGold via-amber-200 to-accentCyan">Algorithmic Analytics</span>
                    </h1>
                    <p class="mt-6 text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto leading-relaxed font-normal">
                        Master Smart Money Concepts (SMC), order flow dynamics, and quantitative analytics through daily live Google Meet interactive mentorship sessions led by <strong class="text-white">Mr. Yusuf</strong>.
                    </p>
                    
                    <div class="mt-10 flex flex-col sm:flex-row justify-center items-center gap-4">
                        <button onclick="openLeadModal('Access AI Tools via Free Partner Account')" class="w-full sm:w-auto bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold px-8 py-4 rounded-xl shadow-xl transition-all text-sm sm:text-base text-center">
                            Access AI Tools via Free Partner Account
                        </button>
                        <button onclick="switchTab('proof')" class="w-full sm:w-auto bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold px-8 py-4 rounded-xl transition-all text-sm sm:text-base">
                            View Live Meet Proofs →
                        </button>
                    </div>

                    <!-- LIVE MEET MOCKUP -->
                    <div class="mt-14 max-w-4xl mx-auto rounded-2xl border border-slate-800 bg-cardBg overflow-hidden shadow-2xl p-3 sm:p-5 glow-gold">
                        <div class="bg-slate-950 rounded-xl p-4 sm:p-6 text-left border border-slate-800/80">
                            <div class="flex flex-wrap items-center justify-between border-b border-slate-800 pb-4 mb-4 gap-2">
                                <div class="flex items-center gap-3">
                                    <span class="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span>
                                    <div>
                                        <h3 class="text-white font-bold text-sm sm:text-base">Google Meet: Nifty & BankNifty Live Execution</h3>
                                        <p class="text-xs text-slate-400">Host: Lead Mentor Mr. Yusuf | Order Flow & SMC Masterclass</p>
                                    </div>
                                </div>
                                <span class="bg-emerald-500/20 text-emerald-400 text-xs px-3 py-1 rounded-full font-mono font-bold border border-emerald-500/30">
                                    🟢 48 Traders Connected
                                </span>
                            </div>

                            <div class="bg-slate-900 rounded-lg p-4 sm:p-6 border border-slate-800 relative min-h-[220px] flex flex-col justify-between">
                                <div class="flex justify-between items-center text-xs font-mono text-slate-400 border-b border-slate-800/60 pb-2">
                                    <span>[LIVE SCREENSHARE] NIFTY 5m Order Block Sweep</span>
                                    <span class="text-accentGold font-bold">FVG Zone Identified</span>
                                </div>

                                <div class="my-6 flex items-end justify-around h-28 px-4 opacity-90">
                                    <div class="flex flex-col items-center gap-1"><div class="w-1 h-6 bg-red-500/40"></div><div class="w-3 h-12 bg-red-500 rounded-sm"></div><div class="w-1 h-4 bg-red-500/40"></div></div>
                                    <div class="flex flex-col items-center gap-1"><div class="w-1 h-4 bg-red-500/40"></div><div class="w-3 h-8 bg-red-500 rounded-sm"></div><div class="w-1 h-3 bg-red-500/40"></div></div>
                                    <div class="flex flex-col items-center gap-1"><div class="w-1 h-8 bg-emerald-500/40"></div><div class="w-3 h-16 bg-emerald-500 rounded-sm"></div><div class="w-1 h-6 bg-emerald-500/40"></div></div>
                                    <div class="flex flex-col items-center gap-1 relative"><span class="absolute -top-6 text-[9px] font-mono bg-accentGold text-slate-950 font-bold px-1.5 py-0.5 rounded">Entry Trigger</span><div class="w-1 h-10 bg-emerald-500/40"></div><div class="w-3 h-20 bg-emerald-500 rounded-sm"></div><div class="w-1 h-4 bg-emerald-500/40"></div></div>
                                    <div class="flex flex-col items-center gap-1"><div class="w-1 h-6 bg-emerald-500/40"></div><div class="w-3 h-14 bg-emerald-500 rounded-sm"></div><div class="w-1 h-2 bg-emerald-500/40"></div></div>
                                </div>

                                <div class="flex items-center justify-between border-t border-slate-800/60 pt-3 text-xs text-slate-400">
                                    <div class="flex items-center gap-3">
                                        <span class="bg-slate-800 p-1.5 rounded-md">🎤 Mic Active</span>
                                        <span class="bg-slate-800 p-1.5 rounded-md hidden sm:inline-block">📷 HD Cam</span>
                                    </div>
                                    <span class="text-accentCyan font-mono text-[11px]">Streamlit Terminal Synced</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            <!-- METRICS -->
            <section class="py-10 bg-slate-900/60 border-b border-slate-800">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                        <div class="p-5 bg-cardBg rounded-xl border border-slate-800"><p class="text-3xl sm:text-4xl font-extrabold text-accentGold">500+</p><p class="text-xs text-slate-400 mt-1 uppercase font-semibold">Active Traders Joined</p></div>
                        <div class="p-5 bg-cardBg rounded-xl border border-slate-800"><p class="text-3xl sm:text-4xl font-extrabold text-emerald-400">120+</p><p class="text-xs text-slate-400 mt-1 uppercase font-semibold">Live Google Meets Held</p></div>
                        <div class="p-5 bg-cardBg rounded-xl border border-slate-800"><p class="text-3xl sm:text-4xl font-extrabold text-accentCyan">100%</p><p class="text-xs text-slate-400 mt-1 uppercase font-semibold">Free Terminal Access</p></div>
                        <div class="p-5 bg-cardBg rounded-xl border border-slate-800"><p class="text-3xl sm:text-4xl font-extrabold text-purple-400">4.9 / 5</p><p class="text-xs text-slate-400 mt-1 uppercase font-semibold">Community Rating</p></div>
                    </div>
                </div>
            </section>

            <!-- PATHWAYS -->
            <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div class="text-center max-w-3xl mx-auto mb-16">
                    <span class="text-accentCyan font-semibold text-xs uppercase tracking-widest">Compliant Onboarding Options</span>
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-white mt-2">Institutional Terminal Pathways</h2>
                    <p class="text-slate-400 text-sm sm:text-base mt-3">Select your preferred compliance pathway to receive complete access to the TradeVortex AI Analytics Suite and daily live mentorship.</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="bg-cardBg border border-slate-800 rounded-2xl p-8 flex flex-col justify-between shadow-xl">
                        <div>
                            <span class="text-emerald-400 text-xs font-semibold uppercase tracking-wider bg-emerald-500/10 px-3 py-1 rounded-md border border-emerald-500/20">Pathway 01</span>
                            <h3 class="text-xl font-bold text-white mt-6">New Partner Account</h3>
                            <p class="text-slate-400 text-sm mt-3 leading-relaxed">Open a fresh Angel One Demat account through our official institutional partner link to unlock 100% complimentary terminal access.</p>
                            <ul class="mt-6 space-y-2 text-xs text-slate-300">
                                <li class="flex items-center gap-2">✓ Free Institutional Terminal License</li>
                                <li class="flex items-center gap-2">✓ Daily Google Meet Class Access</li>
                                <li class="flex items-center gap-2">✓ Zero Monthly Maintenance Fee</li>
                            </ul>
                        </div>
                        <div class="mt-8">
                            <button onclick="openLeadModal('Pathway 1: New Partner Account')" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 px-4 rounded-xl transition-all text-center block text-sm shadow-md">
                                Open Account Free
                            </button>
                        </div>
                    </div>

                    <div class="bg-cardBg border border-slate-800 rounded-2xl p-8 flex flex-col justify-between shadow-xl">
                        <div>
                            <span class="text-accentCyan text-xs font-semibold uppercase tracking-wider bg-cyan-500/10 px-3 py-1 rounded-md border border-cyan-500/20">Pathway 02</span>
                            <h3 class="text-xl font-bold text-white mt-6">Family / Peer Account</h3>
                            <p class="text-slate-400 text-sm mt-3 leading-relaxed">Already have an account in your name? Open a new account for a family member or friend using our link to fulfill onboarding requirements.</p>
                            <ul class="mt-6 space-y-2 text-xs text-slate-300">
                                <li class="flex items-center gap-2">✓ Compliant Multi-User Access</li>
                                <li class="flex items-center gap-2">✓ Live Class Pass Included</li>
                                <li class="flex items-center gap-2">✓ Full Analytics Suite Unlocked</li>
                            </ul>
                        </div>
                        <div class="mt-8">
                            <button onclick="openLeadModal('Pathway 2: Family / Peer Account')" class="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-3.5 px-4 rounded-xl transition-all text-center block text-sm border border-slate-700 shadow-md">
                                Register Family Member
                            </button>
                        </div>
                    </div>

                    <div class="bg-cardBg border border-slate-800 rounded-2xl p-8 flex flex-col justify-between shadow-xl">
                        <div>
                            <span class="text-accentGold text-xs font-semibold uppercase tracking-wider bg-amber-500/10 px-3 py-1 rounded-md border border-amber-500/20">Pathway 03</span>
                            <h3 class="text-xl font-bold text-white mt-6">Direct Terminal Pass</h3>
                            <p class="text-slate-400 text-sm mt-3 leading-relaxed">Prefer not to open a new Demat account? Procure a direct terminal research pass for ₹4,999 via verified WhatsApp channel.</p>
                            <ul class="mt-6 space-y-2 text-xs text-slate-300">
                                <li class="flex items-center gap-2">✓ Direct Educational Terminal Pass</li>
                                <li class="flex items-center gap-2">✓ Immediate Credential Setup</li>
                                <li class="flex items-center gap-2">✓ Dedicated Support Assistance</li>
                            </ul>
                        </div>
                        <div class="mt-8">
                            <a href="https://wa.me/918108433013?text=Bhai%20mujhe%20AI%20Tools%20ka%204999%20wala%20pass%20chahiye" target="_blank" class="w-full bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-3.5 px-4 rounded-xl transition-all text-center block text-sm shadow-md">
                                Acquire Direct Pass (₹4,999)
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            <!-- STUDENT TESTIMONIALS SECTION -->
            <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 bg-slate-900/40 rounded-3xl border border-slate-800 my-10">
                <div class="text-center max-w-3xl mx-auto mb-12">
                    <span class="text-accentGold font-bold text-xs uppercase tracking-widest">Success Stories</span>
                    <h2 class="text-3xl font-extrabold text-white mt-2">What Our Community Traders Say</h2>
                    <p class="text-slate-400 text-sm mt-2">Real feedback from active traders mastering SMC with Mr. Yusuf.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="bg-cardBg p-6 rounded-2xl border border-slate-800">
                        <p class="text-xs text-amber-400 font-bold mb-2">★★★★★</p>
                        <p class="text-slate-300 text-xs italic leading-relaxed">"Yusuf bhai ka SMC mentorship aur FVG mapping session join karne ke baad mere entries bilkul sharp ho gaye hain. Live meets are gold!"</p>
                        <p class="text-white font-bold text-xs mt-4">— Rohit S. <span class="text-slate-500 font-normal">(Mumbai)</span></p>
                    </div>
                    <div class="bg-cardBg p-6 rounded-2xl border border-slate-800">
                        <p class="text-xs text-amber-400 font-bold mb-2">★★★★★</p>
                        <p class="text-slate-300 text-xs italic leading-relaxed">"Streamlit AI terminal tool amazing hai. Options strike selection aur risk calculation ab seconds mein ho jata hai. Highly recommended."</p>
                        <p class="text-white font-bold text-xs mt-4">— Amit K. <span class="text-slate-500 font-normal">(Delhi)</span></p>
                    </div>
                    <div class="bg-cardBg p-6 rounded-2xl border border-slate-800">
                        <p class="text-xs text-amber-400 font-bold mb-2">★★★★★</p>
                        <p class="text-slate-300 text-xs italic leading-relaxed">"Sabse best baat transparency hai. Daily Google Meet par Yusuf bhai khud live chart mark karke dikhate hain."</p>
                        <p class="text-white font-bold text-xs mt-4">— Vishal P. <span class="text-slate-500 font-normal">(Ahmedabad)</span></p>
                    </div>
                </div>
            </section>

            <!-- FAQ SECTION -->
            <section class="max-w-4xl mx-auto px-4 py-16">
                <div class="text-center mb-12">
                    <h2 class="text-3xl font-extrabold text-white">Frequently Asked Questions</h2>
                    <p class="text-slate-400 text-sm mt-2">Got questions? We've got answers.</p>
                </div>
                <div class="space-y-4">
                    <div class="bg-cardBg border border-slate-800 rounded-xl p-5 cursor-pointer" onclick="toggleFaq(this)">
                        <div class="flex justify-between items-center font-bold text-sm text-white">
                            <span>1. How do I get the Google Meet link for live sessions?</span>
                            <span class="text-accentGold text-lg">+</span>
                        </div>
                        <p class="text-slate-400 text-xs mt-3 hidden leading-relaxed">Once you complete your onboarding via partner account or direct pass, you are added to our official VIP community where daily Google Meet links are shared before market hours.</p>
                    </div>
                    <div class="bg-cardBg border border-slate-800 rounded-xl p-5 cursor-pointer" onclick="toggleFaq(this)">
                        <div class="flex justify-between items-center font-bold text-sm text-white">
                            <span>2. Is the Angel One partner account opening free?</span>
                            <span class="text-accentGold text-lg">+</span>
                        </div>
                        <p class="text-slate-400 text-xs mt-3 hidden leading-relaxed">Yes! Opening your Demat account through our official partner link is 100% free with zero annual maintenance charges for the first year.</p>
                    </div>
                    <div class="bg-cardBg border border-slate-800 rounded-xl p-5 cursor-pointer" onclick="toggleFaq(this)">
                        <div class="flex justify-between items-center font-bold text-sm text-white">
                            <span>3. What is included in the AI Analytics Terminal?</span>
                            <span class="text-accentGold text-lg">+</span>
                        </div>
                        <p class="text-slate-400 text-xs mt-3 hidden leading-relaxed">The terminal includes automated Order Block detection, Fair Value Gap (FVG) scanners, live options delta volume tracking, and risk-reward position sizers.</p>
                    </div>
                </div>
            </section>
        </section>

        <!-- PAGE 2: PROOFS -->
        <section id="page-proof" class="page-section hidden py-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center max-w-3xl mx-auto mb-12">
                    <span class="text-accentGold font-bold text-xs uppercase tracking-widest">Verified Transparency</span>
                    <h2 class="text-3xl sm:text-5xl font-extrabold text-white mt-2">Live Google Meet Mentorship Proofs</h2>
                    <p class="text-slate-400 text-sm sm:text-base mt-3">Browse screenshots and chart analysis markups from our daily live trading sessions led by Mr. Yusuf.</p>
                </div>

                <div class="flex flex-wrap justify-center gap-2 sm:gap-3 mb-10">
                    <button onclick="filterProofs('all')" class="proof-filter-btn bg-accentGold text-slate-950 font-bold text-xs px-4 py-2 rounded-lg">All Proofs</button>
                    <button onclick="filterProofs('scalping')" class="proof-filter-btn bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs px-4 py-2 rounded-lg border border-slate-700">Nifty Scalping</button>
                    <button onclick="filterProofs('smc')" class="proof-filter-btn bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs px-4 py-2 rounded-lg border border-slate-700">SMC Masterclass</button>
                    <button onclick="filterProofs('terminal')" class="proof-filter-btn bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold text-xs px-4 py-2 rounded-lg border border-slate-700">AI Terminal Demos</button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    <div class="proof-card scalping bg-cardBg border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
                        <div class="bg-slate-950 p-4 border-b border-slate-800">
                            <div class="bg-slate-900 rounded-lg p-4 aspect-video flex flex-col justify-between border border-slate-800">
                                <div class="flex justify-between items-center text-[10px] text-slate-400"><span>🔴 Live Screen Share</span><span class="font-mono">10:15 AM IST</span></div>
                                <div class="my-auto text-center"><div class="font-mono text-emerald-400 text-sm font-bold">NIFTY 24,500 CE | Order Flow Sweep</div><p class="text-[11px] text-slate-400 mt-1">Live FVG Refinement with 58 Community Members</p></div>
                                <div class="flex justify-between items-center text-[10px] text-slate-500 border-t border-slate-800/80 pt-2"><span>Mentor: Mr. Yusuf</span><span class="text-emerald-400 font-semibold">Verified</span></div>
                            </div>
                        </div>
                        <div class="p-6"><span class="text-accentGold text-xs font-bold uppercase">Session #118</span><h3 class="text-lg font-bold text-white mt-1">Nifty Index Liquidity Sweep & Entry</h3><p class="text-slate-400 text-xs mt-2">Live session mapping out exact equal lows liquidity sweep before the 120 point rally.</p></div>
                    </div>
                    <div class="proof-card smc bg-cardBg border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
                        <div class="bg-slate-950 p-4 border-b border-slate-800">
                            <div class="bg-slate-900 rounded-lg p-4 aspect-video flex flex-col justify-between border border-slate-800">
                                <div class="flex justify-between items-center text-[10px] text-slate-400"><span>🔴 Live Screen Share</span><span class="font-mono">01:45 PM IST</span></div>
                                <div class="my-auto text-center"><div class="font-mono text-accentCyan text-sm font-bold">BANKNIFTY Order Block Mapping</div><p class="text-[11px] text-slate-400 mt-1">15-Min Structure Break + 1-Min FVG Refinement</p></div>
                                <div class="flex justify-between items-center text-[10px] text-slate-500 border-t border-slate-800/80 pt-2"><span>Mentor: Mr. Yusuf</span><span class="text-accentCyan font-semibold">Verified</span></div>
                            </div>
                        </div>
                        <div class="p-6"><span class="text-accentCyan text-xs font-bold uppercase">Session #115</span><h3 class="text-lg font-bold text-white mt-1">BankNifty Institutional Order Block</h3><p class="text-slate-400 text-xs mt-2">Step-by-step breakdown showing how institutional order blocks hold key levels.</p></div>
                    </div>
                    <div class="proof-card terminal bg-cardBg border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
                        <div class="bg-slate-950 p-4 border-b border-slate-800">
                            <div class="bg-slate-900 rounded-lg p-4 aspect-video flex flex-col justify-between border border-slate-800">
                                <div class="flex justify-between items-center text-[10px] text-slate-400"><span>🔴 Terminal Demo</span><span class="font-mono">03:30 PM IST</span></div>
                                <div class="my-auto text-center"><div class="font-mono text-purple-400 text-sm font-bold">TradeVortex Streamlit AI Dashboard</div><p class="text-[11px] text-slate-400 mt-1">Automated Strike Selection & Risk Calculator</p></div>
                                <div class="flex justify-between items-center text-[10px] text-slate-500 border-t border-slate-800/80 pt-2"><span>Mentor: Mr. Yusuf</span><span class="text-purple-400 font-semibold">Verified</span></div>
                            </div>
                        </div>
                        <div class="p-6"><span class="text-purple-400 text-xs font-bold uppercase">Session #112</span><h3 class="text-lg font-bold text-white mt-1">AI Tools Setup & Onboarding</h3><p class="text-slate-400 text-xs mt-2">Live walkthrough guiding academy members on connecting analytics terminal.</p></div>
                    </div>
                </div>
            </div>
        </section>

        <!-- PAGE 3: CURRICULUM -->
        <section id="page-curriculum" class="page-section hidden py-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center max-w-3xl mx-auto mb-16">
                    <span class="text-accentCyan font-bold text-xs uppercase tracking-widest">Syllabus Breakdown</span>
                    <h2 class="text-3xl sm:text-5xl font-extrabold text-white mt-2">Institutional Curriculum Pillars</h2>
                    <p class="text-slate-400 text-sm sm:text-base mt-3">Built strictly on quantitative research and market structure dynamics taught by Mr. Yusuf.</p>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div class="bg-cardBg/60 border border-slate-800 rounded-2xl p-8"><span class="text-accentGold font-mono text-lg font-bold">01</span><h3 class="text-lg font-bold text-white mt-4 mb-2">Market Structure</h3><p class="text-slate-400 text-sm leading-relaxed">Systematic identification of structural breaks (BOS) and character shifts (CHoCH).</p></div>
                    <div class="bg-cardBg/60 border border-slate-800 rounded-2xl p-8"><span class="text-accentCyan font-mono text-lg font-bold">02</span><h3 class="text-lg font-bold text-white mt-4 mb-2">Imbalance & Liquidity</h3><p class="text-slate-400 text-sm leading-relaxed">Precise mapping of Fair Value Gaps (FVG), order blocks, and institutional sweeps.</p></div>
                    <div class="bg-cardBg/60 border border-slate-800 rounded-2xl p-8"><span class="text-emerald-400 font-mono text-lg font-bold">03</span><h3 class="text-lg font-bold text-white mt-4 mb-2">Algorithmic Execution</h3><p class="text-slate-400 text-sm leading-relaxed">Automated strike selection, trend filters, and dynamic risk management calculators.</p></div>
                </div>
            </div>
        </section>

        <!-- PAGE 4: SUPPORT DESK -->
        <section id="page-contact" class="page-section hidden py-16">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="text-center max-w-3xl mx-auto mb-16">
                    <span class="text-emerald-400 font-bold text-xs uppercase tracking-widest">Support Desk</span>
                    <h2 class="text-3xl sm:text-5xl font-extrabold text-white mt-2">Get Assistance & Account Setup</h2>
                    <p class="text-slate-400 text-sm sm:text-base mt-3">Need help with Demat opening or terminal pass? Our team is available directly on WhatsApp.</p>
                </div>
                <div class="bg-cardBg border border-slate-800 rounded-2xl p-8 max-w-2xl mx-auto shadow-xl text-center">
                    <span class="text-emerald-400 text-xs font-bold uppercase tracking-wider bg-emerald-500/10 px-3 py-1 rounded">Instant WhatsApp Support</span>
                    <h3 class="text-2xl font-bold text-white mt-4">Official WhatsApp Line</h3>
                    <p class="text-slate-400 text-xs mt-2">Connect directly with Mr. Yusuf and the TradeVortex onboarding desk.</p>
                    <div class="mt-8 space-y-4 text-xs max-w-xs mx-auto text-left">
                        <div class="flex items-center gap-3 text-slate-350"><span>📱</span><div><p class="text-slate-500 font-semibold">WhatsApp Number</p><p class="text-white font-mono font-bold">+91 81084 33013</p></div></div>
                        <div class="flex items-center gap-3 text-slate-300"><span>👨‍🏫</span><div><p class="text-slate-500 font-semibold">Lead Mentor</p><p class="text-white font-bold">Mr. Yusuf</p></div></div>
                    </div>
                    <div class="mt-8">
                        <a href="https://wa.me/918108433013?text=Hello%20TradeVortex%20Team,%20I%20need%20assistance%20with%20account%20setup" target="_blank" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 px-4 rounded-xl transition-all text-center block text-xs shadow-md">
                            Open WhatsApp Chat Now →
                        </a>
                    </div>
                </div>
            </div>
        </section>

    </main>

    <!-- LEAD CAPTURE MODAL POPUP -->
    <div id="leadModal" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
        <div class="bg-cardBg border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl relative">
            <button onclick="closeLeadModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white font-bold text-lg">✕</button>
            <span class="text-accentGold text-xs font-bold uppercase">Quick Verification</span>
            <h3 class="text-xl font-bold text-white mt-2">Claim Your Terminal Access</h3>
            <p class="text-slate-400 text-xs mt-1">Enter your details to proceed to WhatsApp with pre-filled info.</p>
            
            <form id="leadForm" onsubmit="submitLeadForm(event)" class="mt-6 space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">Your Name</label>
                    <input type="text" id="userName" required placeholder="e.g. Rahul Sharma" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-accentGold">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1">WhatsApp Number</label>
                    <input type="tel" id="userPhone" required placeholder="e.g. 9876543210" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-accentGold">
                </div>
                <button type="submit" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3.5 rounded-xl text-xs transition-all shadow-md mt-2">
                    Proceed to WhatsApp →
                </button>
            </form>
        </div>
    </div>

    <!-- FLOATING WHATSAPP -->
    <a href="https://wa.me/918108433013?text=Hello%20Mr.%20Yusuf,%20I%20want%20to%20join%20TradeVortex%20Academy." target="_blank" class="fixed bottom-6 right-6 z-50 bg-slate-800 hover:bg-slate-700 text-white p-4 rounded-full shadow-2xl border border-slate-700 flex items-center justify-center transition-all hover:scale-110 group glow-emerald">
        <svg class="w-7 h-7 fill-current text-emerald-400" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>
    </a>

    <!-- FOOTER -->
    <footer class="py-12 border-t border-slate-800/80 bg-slate-950 text-center text-xs text-slate-500 max-w-7xl mx-auto px-4 w-full">
        <p class="mb-3 font-medium text-slate-400">© 2026 TradeVortex School of Trading. Lead Mentor: Mr. Yusuf.</p>
        <p class="max-w-3xl mx-auto leading-relaxed text-[11px] text-slate-500">
            Strict Regulatory Disclaimer: All analytical tools, curriculum materials, algorithmic indicators, and live Google Meet mentorship setups are provided exclusively for educational research, technical backtesting, and market structure analysis. TradeVortex does not operate as a SEBI registered investment advisor and does not offer financial advice, tip services, or guaranteed returns. Trading equities, futures, and options involves substantial risk of loss.
        </p>
    </footer>

    <!-- JAVASCRIPT -->
    <script>
        function switchTab(tabId) {
            const pages = document.querySelectorAll('.page-section');
            pages.forEach(page => page.classList.add('hidden'));
            const activePage = document.getElementById('page-' + tabId);
            if (activePage) activePage.classList.remove('hidden');

            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active-nav-link'));
            const activeDesktopNav = document.getElementById('nav-' + tabId);
            if (activeDesktopNav) activeDesktopNav.classList.add('active-nav-link');

            document.querySelectorAll('.nav-mob-btn').forEach(btn => btn.classList.remove('active-nav-link'));
            const activeMobileNav = document.getElementById('mob-nav-' + tabId);
            if (activeMobileNav) activeMobileNav.classList.add('active-nav-link');

            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function filterProofs(category) {
            document.querySelectorAll('.proof-card').forEach(card => {
                card.style.display = (category === 'all' || card.classList.contains(category)) ? 'block' : 'none';
            });
            document.querySelectorAll('.proof-filter-btn').forEach(btn => {
                btn.classList.remove('bg-accentGold', 'text-slate-950');
                btn.classList.add('bg-slate-800', 'text-slate-300');
            });
            event.target.classList.remove('bg-slate-800', 'text-slate-300');
            event.target.classList.add('bg-accentGold', 'text-slate-950');
        }

        function toggleFaq(element) {
            const p = element.querySelector('p');
            const span = element.querySelector('span:last-child');
            if (p.classList.contains('hidden')) {
                p.classList.remove('hidden');
                span.textContent = '−';
            } else {
                p.classList.add('hidden');
                span.textContent = '+';
            }
        }

        let selectedPathway = '';
        function openLeadModal(pathway) {
            selectedPathway = pathway;
            document.getElementById('leadModal').classList.remove('hidden');
        }
        function closeLeadModal() {
            document.getElementById('leadModal').classList.add('hidden');
        }
        function submitLeadForm(e) {
            e.preventDefault();
            const name = document.getElementById('userName').value;
            const phone = document.getElementById('userPhone').value;
            const text = encodeURIComponent(`Hello Mr. Yusuf, my name is ${name} (${phone}). I want to join via: ${selectedPathway}`);
            window.open(`https://wa.me/918108433013?text=${text}`, '_blank');
            closeLeadModal();
        }

        // Countdown Timer
        let totalSeconds = 3 * 3600 + 45 * 60 + 12;
        setInterval(() => {
            if (totalSeconds > 0) totalSeconds--;
            let h = Math.floor(totalSeconds / 3600);
            let m = Math.floor((totalSeconds % 3600) / 60);
            let s = totalSeconds % 60;
            document.getElementById('countdown').textContent = 
                String(h).padStart(2,'0') + 'h : ' + String(m).padStart(2,'0') + 'm : ' + String(s).padStart(2,'0') + 's';
        }, 1000);
    </script>
</body>
</html>
