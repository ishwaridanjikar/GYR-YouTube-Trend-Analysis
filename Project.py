from flask import Flask, render_template_string, request, send_file, redirect, url_for, session
import pandas as pd
import json
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import warnings
import base64
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from PIL import Image as PILImage

# Suppress warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)
app.secret_key = 'youtube_analyzer_secret_key'

# HTML for landing page (modified from user's code)
LANDING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GYR - Analytics Made Simple</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --midnight: #0A0E27;
            --slate: #1A1F3A;
            --lavender: #8B7FD8;
            --coral: #FF6B6B;
            --cream: #FFF8F0;
            --gold: #FFD700;
            --mist: #E8E4F3;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'DM Sans', sans-serif;
            background: linear-gradient(135deg, var(--midnight) 0%, var(--slate) 100%);
            color: var(--cream);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* Animated background elements */
        .bg-orbs {
            position: fixed;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }

        .orb {
            position: absolute;
            border-radius: 50%;
            opacity: 0.15;
            filter: blur(60px);
            animation: float 20s infinite ease-in-out;
        }

        .orb-1 {
            width: 400px;
            height: 400px;
            background: var(--lavender);
            top: -100px;
            left: -100px;
            animation-delay: 0s;
        }

        .orb-2 {
            width: 300px;
            height: 300px;
            background: var(--coral);
            bottom: -50px;
            right: -50px;
            animation-delay: 5s;
        }

        .orb-3 {
            width: 250px;
            height: 250px;
            background: var(--gold);
            top: 50%;
            right: 10%;
            animation-delay: 10s;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -30px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.9); }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 40px;
            position: relative;
            z-index: 1;
        }

        /* Header */
        header {
            padding: 40px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 2px;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--lavender), var(--coral));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            animation: pulse 3s infinite;
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(139, 127, 216, 0.7); }
            50% { box-shadow: 0 0 0 20px rgba(139, 127, 216, 0); }
        }

        .eye-icon {
            width: 24px;
            height: 24px;
            color: white;
        }

        nav a {
            color: var(--mist);
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            transition: color 0.3s;
        }

        nav a:hover {
            color: var(--lavender);
        }

        /* Hero Section */
        .hero {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: calc(100vh - 200px);
            padding: 60px 0;
            text-align: center;
        }

        .hero-content {
            max-width: 800px;
            animation: fadeInUp 1s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h1 {
            font-family: 'Playfair Display', serif;
            font-size: 82px;
            font-weight: 900;
            line-height: 0.95;
            margin-bottom: 30px;
            background: linear-gradient(135deg, var(--cream) 0%, var(--lavender) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 22px;
            color: var(--mist);
            margin-bottom: 50px;
            font-weight: 400;
            line-height: 1.6;
            margin-left: auto;
            margin-right: auto;
        }

        .cta-button {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            background: linear-gradient(135deg, var(--lavender), var(--coral));
            color: white;
            padding: 20px 40px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 700;
            font-size: 16px;
            letter-spacing: 0.5px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 40px rgba(139, 127, 216, 0.3);
            position: relative;
            overflow: hidden;
        }

        .cta-button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }

        .cta-button:hover::before {
            left: 100%;
        }

        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 50px rgba(139, 127, 216, 0.5);
        }

        .arrow {
            transition: transform 0.3s;
        }

        .cta-button:hover .arrow {
            transform: translateX(5px);
        }

        /* Features */
        .features {
            display: flex;
            gap: 30px;
            margin-top: 50px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .feature {
            display: flex;
            align-items: center;
            gap: 12px;
            color: var(--mist);
            font-size: 15px;
        }

        .check-icon {
            width: 24px;
            height: 24px;
            background: linear-gradient(135deg, var(--lavender), var(--coral));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        /* Responsive */
        @media (max-width: 1024px) {
            h1 {
                font-size: 64px;
            }
        }

        @media (max-width: 640px) {
            .container {
                padding: 0 20px;
            }

            h1 {
                font-size: 48px;
            }

            .subtitle {
                font-size: 18px;
            }
        }
    </style>
</head>
<body>
    <div class="bg-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
    </div>

    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon">
                    <svg class="eye-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                </div>
                <span>GYR</span>
            </div>
            <nav>
                <a href="#features">Features</a>
            </nav>
        </header>

        <main class="hero">
            <div class="hero-content">
                <h1>Get Your Report</h1>
                <p class="subtitle">Transform your CSV data into beautiful, actionable insights in seconds. No setup, no complexity — just results.</p>
                
                <a href="/upload" class="cta-button">
                    Upload CSV File
                    <svg class="arrow" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                </a>

                <div class="features">
                    <div class="feature">
                        <div class="check-icon">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                        </div>
                        <span>Instant Analysis</span>
                    </div>
                    <div class="feature">
                        <div class="check-icon">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                        </div>
                        <span>Visual Reports</span>
                    </div>
                    <div class="feature">
                        <div class="check-icon">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3">
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                        </div>
                        <span>Export Ready</span>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
"""

# HTML for upload page (modified)
UPLOAD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload CSV - GYR</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --midnight: #0A0E27;
            --slate: #1A1F3A;
            --lavender: #8B7FD8;
            --coral: #FF6B6B;
            --cream: #FFF8F0;
            --gold: #FFD700;
            --mist: #E8E4F3;
            --success: #4ECDC4;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'DM Sans', sans-serif;
            background: linear-gradient(135deg, var(--midnight) 0%, var(--slate) 100%);
            color: var(--cream);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        .bg-orbs {
            position: fixed;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }

        .orb {
            position: absolute;
            border-radius: 50%;
            opacity: 0.12;
            filter: blur(60px);
            animation: float 20s infinite ease-in-out;
        }

        .orb-1 {
            width: 350px;
            height: 350px;
            background: var(--lavender);
            top: 10%;
            right: -50px;
            animation-delay: 0s;
        }

        .orb-2 {
            width: 300px;
            height: 300px;
            background: var(--coral);
            bottom: 10%;
            left: -50px;
            animation-delay: 7s;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            50% { transform: translate(40px, -40px) scale(1.15); }
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 60px;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 28px;
            font-weight: 700;
            letter-spacing: 2px;
            text-decoration: none;
            color: var(--cream);
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--lavender), var(--coral));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: pulse 3s infinite;
        }

        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(139, 127, 216, 0.7); }
            50% { box-shadow: 0 0 0 20px rgba(139, 127, 216, 0); }
        }

        .back-link {
            color: var(--mist);
            text-decoration: none;
            font-size: 15px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: color 0.3s;
        }

        .back-link:hover {
            color: var(--lavender);
        }

        .upload-section {
            flex: 1;
            display: flex;
            flex-direction: column;
            animation: fadeInUp 0.8s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h1 {
            font-family: 'Playfair Display', serif;
            font-size: 56px;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 20px;
            background: linear-gradient(135deg, var(--cream) 0%, var(--lavender) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 18px;
            color: var(--mist);
            margin-bottom: 50px;
            opacity: 0.8;
        }

        .drop-zone {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border: 2px dashed rgba(139, 127, 216, 0.3);
            border-radius: 24px;
            padding: 80px 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .drop-zone::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at center, rgba(139, 127, 216, 0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s;
        }

        .drop-zone:hover::before,
        .drop-zone.drag-over::before {
            opacity: 1;
        }

        .drop-zone:hover {
            border-color: var(--lavender);
            background: rgba(139, 127, 216, 0.05);
            transform: translateY(-4px);
        }

        .drop-zone.drag-over {
            border-color: var(--lavender);
            background: rgba(139, 127, 216, 0.08);
            transform: scale(1.02);
        }

        .upload-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, var(--lavender), var(--coral));
            border-radius: 50%;
            transition: transform 0.4s;
        }

        .drop-zone:hover .upload-icon {
            transform: translateY(-10px);
        }

        .drop-zone-text h3 {
            font-size: 24px;
            margin-bottom: 12px;
            font-weight: 700;
        }

        .drop-zone-text p {
            font-size: 16px;
            color: var(--mist);
            opacity: 0.7;
        }

        .or-divider {
            display: flex;
            align-items: center;
            gap: 20px;
            margin: 40px 0;
            font-size: 14px;
            color: var(--mist);
            opacity: 0.5;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .or-divider::before,
        .or-divider::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
        }

        .browse-btn {
            width: 100%;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            color: var(--cream);
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .browse-btn:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--lavender);
            transform: translateY(-2px);
        }

        .file-input {
            display: none;
        }

        .file-info {
            margin-top: 40px;
            padding: 30px;
            background: rgba(78, 205, 196, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(78, 205, 196, 0.3);
            border-radius: 20px;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            pointer-events: none;
        }

        .file-info.show {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }

        .file-info-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }

        .file-details {
            flex: 1;
        }

        .file-name {
            font-size: 18px;
            font-weight: 700;
            color: var(--success);
            margin-bottom: 8px;
            word-break: break-all;
        }

        .file-size {
            font-size: 14px;
            color: var(--mist);
            opacity: 0.7;
        }

        .remove-btn {
            background: rgba(255, 107, 107, 0.2);
            border: none;
            color: var(--coral);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .remove-btn:hover {
            background: rgba(255, 107, 107, 0.3);
        }

        .file-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--success), var(--lavender));
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }

        .submit-btn {
            width: 100%;
            padding: 22px;
            background: linear-gradient(135deg, var(--lavender), var(--coral));
            border: none;
            border-radius: 16px;
            color: white;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 30px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 10px 40px rgba(139, 127, 216, 0.3);
            opacity: 0;
            transform: translateY(20px);
            pointer-events: none;
            position: relative;
            overflow: hidden;
        }

        .submit-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }

        .submit-btn:hover::before {
            left: 100%;
        }

        .submit-btn.show {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }

        .submit-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 50px rgba(139, 127, 216, 0.5);
        }

        @media (max-width: 640px) {
            h1 {
                font-size: 42px;
            }

            .drop-zone {
                padding: 60px 30px;
            }

            .upload-icon {
                width: 60px;
                height: 60px;
            }

            .drop-zone-text h3 {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="bg-orbs">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
    </div>

    <div class="container">
        <header>
            <div class="logo">
                <div class="logo-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                </div>
                <span>GYR</span>
            </div>

            <a href="/" class="back-link">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg>
                Back
            </a>
        </header>

        <main class="upload-section">
            <h1>Upload Your Data</h1>
            <p class="subtitle">Drop your CSV file below and we'll transform it into insights</p>

            <form action="/analyze" method="post" enctype="multipart/form-data">
                <div class="drop-zone" id="dropZone">
                    <div class="upload-icon">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                    </div>
                    <div class="drop-zone-text">
                        <h3>Drag & drop your CSV file here</h3>
                        <p>or click to browse</p>
                    </div>
                </div>

                <div class="or-divider">or</div>

                <input type="file" id="fileInput" name="file" class="file-input" accept=".csv">
                <button class="browse-btn" id="browseBtn" type="button">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                    </svg>
                    Browse Files
                </button>

                <div class="file-info" id="fileInfo">
                    <div class="file-icon">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                            <polyline points="14 2 14 8 20 8"></polyline>
                            <line x1="12" y1="18" x2="12" y2="12"></line>
                            <line x1="9" y1="15" x2="15" y2="15"></line>
                        </svg>
                    </div>
                    <div class="file-info-header">
                        <div class="file-details">
                            <div class="file-name" id="fileName"></div>
                            <div class="file-size" id="fileSize"></div>
                        </div>
                        <button class="remove-btn" id="removeBtn" type="button">Remove</button>
                    </div>
                </div>

                <button class="submit-btn" id="submitBtn" type="submit">
                    Generate Report
                    <svg style="margin-left: 8px;" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                </button>
            </form>
        </main>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const submitBtn = document.getElementById('submitBtn');
        const removeBtn = document.getElementById('removeBtn');

        let selectedFile = null;

        browseBtn.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });

        removeBtn.addEventListener('click', () => {
            selectedFile = null;
            fileInput.value = '';
            fileInfo.classList.remove('show');
            submitBtn.classList.remove('show');
        });

        function handleFiles(files) {
            if (files.length === 0) return;

            const file = files[0];
            
            if (!file.name.endsWith('.csv')) {
                alert('Please upload a CSV file');
                return;
            }

            selectedFile = file;
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            
            setTimeout(() => {
                fileInfo.classList.add('show');
                setTimeout(() => {
                    submitBtn.classList.add('show');
                }, 200);
            }, 100);
        }

        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }
    </script>
</body>
</html>
"""

def load_data(file_path, cat_path=None):
    # Load categories if available
    cat_dict = {}
    if cat_path and os.path.exists(cat_path):
        try:
            with open(cat_path, encoding='utf-8') as f:
                data = json.load(f)
            cat_dict = {int(item['id']): item['snippet']['title'] for item in data['items']}
        except:
            pass

    # Load CSV
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')

    # Map categories if available
    if cat_dict:
        df['category'] = df['category_id'].map(cat_dict)

    # Data cleaning
    df['trending_date'] = pd.to_datetime(df['trending_date'], format='%y.%d.%m', errors='coerce')
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce').dt.tz_localize(None)
    if 'trending_date' in df and 'publish_time' in df:
        df['days_to_trend'] = (df['trending_date'] - df['publish_time']).dt.days
    df.dropna(subset=['views', 'likes', 'dislikes', 'comment_count'], inplace=True)

    return df

def generate_plots(df):
    plots = []
    # Correlation
    plt.figure()
    corr = df[['views', 'likes', 'dislikes', 'comment_count']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    plots.append(f"data:image/png;base64,{plot_data}")
    plt.close()

    # Views by category
    if 'category' in df:
        plt.figure(figsize=(12,6))
        sns.barplot(x='category', y='views', data=df.groupby('category')['views'].mean().reset_index())
        plt.xticks(rotation=45)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        plots.append(f"data:image/png;base64,{plot_data}")
        plt.close()

    # Engagement
    df['engagement_rate'] = (df['likes'] + df['dislikes'] + df['comment_count']) / df['views']
    plt.figure()
    sns.scatterplot(x='views', y='engagement_rate', data=df)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_data = base64.b64encode(buf.read()).decode('utf-8')
    plots.append(f"data:image/png;base64,{plot_data}")
    plt.close()

    # Title length
    if 'title' in df:
        df['title_length'] = df['title'].str.len()
        plt.figure()
        sns.histplot(df['title_length'])
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        plots.append(f"data:image/png;base64,{plot_data}")
        plt.close()

    # Tags count
    if 'tags' in df:
        df['tags_count'] = df['tags'].str.split('|').str.len()
        plt.figure()
        sns.scatterplot(x='tags_count', y='views', data=df)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        plots.append(f"data:image/png;base64,{plot_data}")
        plt.close()

    # Keywords
    if 'description' in df:
        def extract_keywords(description):
            if pd.isna(description):
                return []
            soup = BeautifulSoup(description, 'html.parser')
            text = soup.get_text()
            keywords = ['music', 'fun', 'viral', 'challenge', 'tutorial']
            return [kw for kw in keywords if kw.lower() in text.lower()]

        df['keywords'] = df['description'].apply(extract_keywords)
        df['keyword_count'] = df['keywords'].str.len()
        plt.figure()
        sns.scatterplot(x='keyword_count', y='views', data=df)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plot_data = base64.b64encode(buf.read()).decode('utf-8')
        plots.append(f"data:image/png;base64,{plot_data}")
        plt.close()

    return plots

def generate_pdf(df, plots):
    pdf_path = os.path.join(os.getcwd(), 'static', 'report.pdf')
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Courier'  # Monospaced font for better formatting
    styles['Normal'].fontSize = 10
    story = []

    # Title
    story.append(Paragraph("YouTube Trending Video Analysis Report", styles['Title']))
    story.append(Spacer(1, 12))

    # Data Summary
    story.append(Paragraph("Data Summary:", styles['Heading2']))
    summary_df = df.describe().round(2)
    data = [['Statistic'] + summary_df.columns.tolist()] + [[idx] + row.tolist() for idx, row in summary_df.iterrows()]
    colWidths = [80] + [70] * len(summary_df.columns)
    table = Table(data, colWidths=colWidths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    # Key Insights
    story.append(Paragraph("Key Insights:", styles['Heading2']))
    insights = [
        "- High engagement (likes/comments) often leads to more views.",
        "- Certain categories like Music dominate trending lists.",
        "- Videos with specific keywords or tags may trend faster.",
        "- Analyze title length and publish timing for better reach."
    ]
    for insight in insights:
        story.append(Paragraph(insight, styles['Normal']))
    story.append(Spacer(1, 12))

    # Plots
    story.append(Paragraph("Plots:", styles['Heading2']))
    for plot in plots:
        decoded = base64.b64decode(plot.split(',')[1])
        img = Image(io.BytesIO(decoded))
        img.drawHeight = 300
        img.drawWidth = 500
        story.append(img)
        story.append(Spacer(1, 12))

    doc.build(story)

@app.route('/')
def landing():
    return LANDING_HTML

@app.route('/upload')
def upload():
    return UPLOAD_HTML

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400
    if not file.filename.endswith('.csv'):
        return "Please upload a CSV file", 400
    
    # Save uploaded file temporarily
    file_path = 'static/uploaded.csv'
    file.save(file_path)
    
    try:
        # Load data
        df = load_data(file_path)
        
        summary_csv = df.describe().to_csv()
        session['summary_csv'] = summary_csv
        
        # Generate plots
        plots = generate_plots(df)
        
        # Generate PDF
        generate_pdf(df, plots)
        
        # Render results
        results_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Analysis Results - GYR</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #0A0E27; color: #FFF8F0; padding: 20px; }}
                .plot {{ margin: 20px 0; }}
                .download {{ margin: 20px 0; }}
                a {{ color: #8B7FD8; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                pre {{ background: #1A1F3A; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                ul {{ list-style-type: disc; margin-left: 20px; }}
            </style>
        </head>
        <body>
            <h1>Analysis Results</h1>
            <h2>Data Summary</h2>
            <pre>{df.describe().to_string()}</pre>
            <h2>Plots</h2>
            {"".join(f'<div class="plot"><img src="{plot}" alt="Plot" style="max-width: 100%; height: auto;"></div>' for plot in plots)}
            <h2>Key Insights</h2>
            <ul>
                <li>High engagement (likes/comments) often leads to more views.</li>
                <li>Certain categories like Music dominate trending lists.</li>
                <li>Videos with specific keywords or tags may trend faster.</li>
                <li>Analyze title length and publish timing for better reach.</li>
            </ul>
            <div class="download">
                <a href="/download_pdf">Download Full PDF Report</a> | 
                <a href="/download_csv">Download CSV Summary</a>
            </div>
            <a href="/">Back to Home</a>
        </body>
        </html>
        """
        return results_html
    except Exception as e:
        return f"An error occurred during analysis: {str(e)}", 500

@app.route('/download_pdf')
def download_pdf():
    pdf_path = os.path.join(os.getcwd(), 'static', 'report.pdf')
    try:
        return send_file(pdf_path, as_attachment=True, download_name='report.pdf')
    except FileNotFoundError:
        return "Report not found. Please generate the report first.", 404

@app.route('/download_csv')
def download_csv():
    if 'summary_csv' not in session:
        return "Summary not found. Please generate the report first.", 404
    return send_file(io.BytesIO(session['summary_csv'].encode()), as_attachment=True, download_name='summary.csv', mimetype='text/csv')





