/**
 * Content script for the Toxic Language Detector Extension
 * Runs on supported social media platforms and analyzes comments
 */

// Định nghĩa các màu và nhãn cho từng loại phân loại
const CATEGORY_STYLES = {
  clean: {
    color: '#4CAF50',  // Green
    label: 'Bình thường',
    className: 'toxic-indicator-clean'
  },
  offensive: {
    color: '#FF9800',  // Orange 
    label: 'Xúc phạm',
    className: 'toxic-indicator-offensive'
  },
  hate: {
    color: '#F44336',  // Red
    label: 'Thù ghét',
    className: 'toxic-indicator-hate'
  },
  spam: {
    color: '#9C27B0',  // Purple
    label: 'Spam',
    className: 'toxic-indicator-spam'
  }
};

// Configuration
const PLATFORMS = {
  FACEBOOK: "facebook",
  YOUTUBE: "youtube",
  TWITTER: "twitter"
};

// Detect current platform
let currentPlatform = '';
if (window.location.hostname.includes("facebook.com")) {
  currentPlatform = PLATFORMS.FACEBOOK;
} else if (window.location.hostname.includes("youtube.com") || window.location.hostname.includes("youtu.be")) {
  currentPlatform = PLATFORMS.YOUTUBE;
} else if (window.location.hostname.includes("twitter.com") || window.location.hostname.includes("x.com")) {
  currentPlatform = PLATFORMS.TWITTER;
}
console.log(`Detected platform: ${currentPlatform}`);

// Extension state
let extensionEnabled = true;
let toxicThreshold = 0.7;
let highlightToxic = true;
let platformEnabled = true;
let displayOptions = {
  showClean: true,
  showOffensive: true, 
  showHate: true,
  showSpam: true
};

// Cache for processed comments
const processedComments = new Set();

// Initialize extension
initialize();

/**
 * Initialize the extension
 */
function initialize() {
  // Load settings from storage
  chrome.storage.sync.get(null, (data) => {
    extensionEnabled = data.enabled !== undefined ? data.enabled : true;
    toxicThreshold = data.threshold || 0.7;
    highlightToxic = data.highlightToxic !== undefined ? data.highlightToxic : true;
    
    // Khởi tạo displayOptions
    displayOptions = data.displayOptions || {
      showClean: true,
      showOffensive: true,
      showHate: true,
      showSpam: true
    };

    if (data.platforms) {
      switch (currentPlatform) {
        case PLATFORMS.FACEBOOK:
          platformEnabled = data.platforms.facebook !== undefined ? data.platforms.facebook : true;
          break;
        case PLATFORMS.YOUTUBE:
          platformEnabled = data.platforms.youtube !== undefined ? data.platforms.youtube : true;
          break;
        case PLATFORMS.TWITTER:
          platformEnabled = data.platforms.twitter !== undefined ? data.platforms.twitter : true;
          break;
      }
    }
    
    // Start observing comments if extension is enabled
    if (extensionEnabled && platformEnabled) {
      startObservingComments();
    }
  });
  
  // Listen for setting changes
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.enabled) {
      extensionEnabled = changes.enabled.newValue;
      
      if (extensionEnabled && platformEnabled) {
        startObservingComments();
      } else {
        stopObservingComments();
      }
    }
    
    if (changes.threshold) {
      toxicThreshold = changes.threshold.newValue;
    }
    
    if (changes.highlightToxic) {
      highlightToxic = changes.highlightToxic.newValue;
    }
    
    if (changes.platforms) {
      const platforms = changes.platforms.newValue;
      
      switch (currentPlatform) {
        case PLATFORMS.FACEBOOK:
          platformEnabled = platforms.facebook;
          break;
        case PLATFORMS.YOUTUBE:
          platformEnabled = platforms.youtube;
          break;
        case PLATFORMS.TWITTER:
          platformEnabled = platforms.twitter;
          break;
      }
      
      if (extensionEnabled && platformEnabled) {
        startObservingComments();
      } else {
        stopObservingComments();
      }
    }
  });
}

// Observer instances
let commentObserver = null;

/**
 * Start observing comments on the page
 */
function startObservingComments() {
  if (commentObserver) {
    return;
  }
  
  // Cấu hình chi tiết hơn cho MutationObserver
  commentObserver = new MutationObserver((mutations) => {
    const commentSelectors = getCommentSelectors();
    
    for (const mutation of mutations) {
      // Xử lý các nodes mới được thêm vào
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        for (const node of mutation.addedNodes) {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Tìm kiếm comments trong node mới
            const comments = node.matches(commentSelectors) ? 
              [node] : Array.from(node.querySelectorAll(commentSelectors));
            
            for (const comment of comments) {
              processComment(comment);
            }
          }
        }
      }
      
      // Xử lý thay đổi thuộc tính (quan trọng cho Twitter)
      if (mutation.type === 'attributes' && mutation.target.nodeType === Node.ELEMENT_NODE) {
        const target = mutation.target;
        // Kiểm tra nếu target là comment hoặc chứa comments
        if (target.matches(commentSelectors)) {
          processComment(target);
        } else {
          const comments = Array.from(target.querySelectorAll(commentSelectors));
          for (const comment of comments) {
            processComment(comment);
          }
        }
      }
    }
  });
  
  // Theo dõi cả childList và attributes
  commentObserver.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['data-testid', 'id', 'class'] // Các thuộc tính quan trọng
  });
  
  // Xử lý các comments hiện có
  processExistingComments();
}

/**
 * Stop observing comments
 */
function stopObservingComments() {
  if (commentObserver) {
    commentObserver.disconnect();
    commentObserver = null;
  }
}

/**
 * Handle DOM changes
 * @param {MutationRecord[]} mutations - Mutation records
 */
function handleDOMChanges(mutations) {
  if (!extensionEnabled || !platformEnabled) {
    return;
  }
  
  const commentSelectors = getCommentSelectors();
  
  // Check if any new comments were added
  for (const mutation of mutations) {
    if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
      for (const node of mutation.addedNodes) {
        if (node.nodeType === Node.ELEMENT_NODE) {
          // Check if this node is a comment or contains comments
          const comments = node.matches(commentSelectors) ? 
            [node] : Array.from(node.querySelectorAll(commentSelectors));
          
          for (const comment of comments) {
            processComment(comment);
          }
        }
      }
    }
  }
}

/**
 * Process existing comments when the extension starts
 */
function processExistingComments() {
  const commentSelectors = getCommentSelectors();
  const comments = document.querySelectorAll(commentSelectors);
  
  for (const comment of comments) {
    processComment(comment);
  }
}

/**
 * Get comment selectors for current platform
 * @returns {string} - CSS selector
 */
function getCommentSelectors() {
  switch (currentPlatform) {
    case PLATFORMS.FACEBOOK:
      return '.x1y1aw1k div[dir="auto"], .userContentWrapper .commentable_item';
    case PLATFORMS.YOUTUBE:
      // Selectors cập nhật cho YouTube
      return 'ytd-comment-renderer #content-text, yt-formatted-string#content-text, ytd-comment-thread-renderer yt-formatted-string#content-text';
    case PLATFORMS.TWITTER:
      // Selectors cập nhật cho Twitter
      return '[data-testid="tweetText"], div[lang][dir="auto"]';
    default:
      return '';
  }
}

/**
 * Process a comment element
 * @param {Element} commentElement - The comment DOM element
 */
function processComment(commentElement) {

  console.log("Processing comment:", commentElement);
  
  // Xử lý dành riêng cho từng nền tảng
  if (currentPlatform === PLATFORMS.YOUTUBE) {
    processYouTubeComment(commentElement);
    return;
  } else if (currentPlatform === PLATFORMS.TWITTER) {
    processTwitterComment(commentElement);
    return;
  }

  const commentId = getCommentId(commentElement);
  
  // Skip if already processed
  if (!commentId || processedComments.has(commentId)) {
    return;
  }
  
  processedComments.add(commentId);
  
  // Get comment text
  const commentText = getCommentText(commentElement);
  
  if (!commentText || commentText.trim().length < 5) {
    return;
  }
  
  console.log(`Analyzing comment: ${commentText.substring(0, 50)}...`);
  
  // Analyze comment
  chrome.runtime.sendMessage({
    action: "analyzeText",
    text: commentText,
    platform: currentPlatform,
    commentId: commentId
  }, (response) => {
    if (response && !response.error) {
      // Apply visual changes based on prediction
      applyToxicityIndicator(commentElement, response);
      
      // Log for debugging
      console.log(`Processed comment: [${response.prediction}] ${commentText.substring(0, 50)}...`);
    } else if (response && response.error) {
      console.error("Error analyzing comment:", response.error);
    }
  });
}

/**
 * Xử lý đặc biệt cho YouTube comments
 * @param {Element} commentElement - Element chứa comment
 */
function processYouTubeComment(commentElement) {
  // YouTube comments thường có text trong yt-formatted-string
  const textElement = commentElement.querySelector('yt-formatted-string#content-text');
  if (!textElement) return;
  
  const commentText = textElement.textContent.trim();
  if (!commentText || commentText.length < 5) return;
  
  // Tạo ID duy nhất cho comment YouTube
  const commentRenderer = commentElement.closest('ytd-comment-renderer');
  const commentId = commentRenderer ? commentRenderer.id : `yt-${hashString(commentText)}`;
  
  // Kiểm tra xem comment đã được xử lý chưa
  if (processedComments.has(commentId)) {
    return;
  }
  
  processedComments.add(commentId);
  
  // Tiến hành phân tích
  chrome.runtime.sendMessage({
    action: "analyzeText",
    text: commentText,
    platform: PLATFORMS.YOUTUBE,
    commentId: commentId
  }, (response) => {
    if (response && !response.error) {
      console.log("YouTube comment processed:", response);
      applyToxicityIndicator(textElement, response);
    } else {
      console.error("Error processing YouTube comment:", response ? response.error : "No response");
    }
  });
}

/**
 * Xử lý đặc biệt cho Twitter tweets/replies
 * @param {Element} commentElement - Element chứa tweet/reply
 */
function processTwitterComment(commentElement) {
  // Twitter có nhiều cấu trúc khác nhau, cần kiểm tra cẩn thận
  if (!commentElement.textContent || commentElement.textContent.trim().length < 5) return;
  
  // Tạo ID duy nhất cho tweet
  const tweetArticle = commentElement.closest('article[data-testid="tweet"]');
  const tweetId = tweetArticle ? 
                tweetArticle.getAttribute('aria-labelledby') : 
                `twitter-${hashString(commentElement.textContent)}`;
  
  // Kiểm tra xem tweet đã được xử lý chưa
  if (processedComments.has(tweetId)) {
    return;
  }
  
  processedComments.add(tweetId);
  
  // Loại bỏ các elements không mong muốn (như emoji, media)
  const commentText = commentElement.textContent.trim();
  
  chrome.runtime.sendMessage({
    action: "analyzeText",
    text: commentText,
    platform: PLATFORMS.TWITTER,
    commentId: tweetId
  }, (response) => {
    if (response && !response.error) {
      console.log("Twitter comment processed:", response);
      applyToxicityIndicator(commentElement, response);
    } else {
      console.error("Error processing Twitter comment:", response ? response.error : "No response");
    }
  });
}

/**
 * Get a unique ID for the comment
 * @param {Element} commentElement - The comment DOM element
 * @returns {string} - Comment ID or null
 */
function getCommentId(commentElement) {
  // Attempt to find an ID based on the platform
  switch (currentPlatform) {
    case PLATFORMS.FACEBOOK:
      // Facebook doesn't expose comment IDs directly, create a hash from content
      const fbText = getCommentText(commentElement);
      return fbText ? `fb-${hashString(fbText)}` : null;
      
    case PLATFORMS.YOUTUBE:
      // Find comment ID from ancestor
      const ytCommentRenderer = commentElement.closest('ytd-comment-renderer');
      return ytCommentRenderer ? ytCommentRenderer.id : null;
      
    case PLATFORMS.TWITTER:
      // Find tweet ID from ancestor
      const tweet = commentElement.closest('article');
      return tweet ? tweet.getAttribute('data-tweet-id') : null;
      
    default:
      return null;
  }
}

/**
 * Get comment text
 * @param {Element} commentElement - The comment DOM element
 * @returns {string} - Comment text
 */
function getCommentText(commentElement) {
  return commentElement.textContent || '';
}


/**
 * Apply toxicity indicator to comment
 * @param {Element} commentElement - The comment DOM element
 * @param {Object} prediction - The prediction result
 */
function applyToxicityIndicator(commentElement, prediction) {
  // Get settings
  chrome.storage.sync.get(['highlightToxic', 'displayOptions'], (data) => {
    const highlightToxic = data.highlightToxic !== undefined ? data.highlightToxic : true;
    const displayOptions = data.displayOptions || {
      showClean: true,
      showOffensive: true,
      showHate: true,
      showSpam: true
    };
    
    // Get category from prediction
    const categoryNames = ["clean", "offensive", "hate", "spam"];
    const category = categoryNames[prediction.prediction] || "unknown";
    
    // Check if we should display this category
    const shouldDisplay = category === "clean" ? displayOptions.showClean :
                          category === "offensive" ? displayOptions.showOffensive :
                          category === "hate" ? displayOptions.showHate :
                          category === "spam" ? displayOptions.showSpam : false;
    
    // Only proceed if highlighting is enabled and we should display this category
    if (!highlightToxic || !shouldDisplay) {
      return;
    }
    
    // Get style for this category
    const style = CATEGORY_STYLES[category] || CATEGORY_STYLES.clean;
    
    // Create toxicity indicator
    const indicator = document.createElement('div');
    indicator.className = `toxic-indicator ${style.className}`;
    indicator.style.backgroundColor = style.color;
    indicator.textContent = style.label;
    
    // Add tooltip
    indicator.title = `Phân loại: ${style.label} (${(prediction.confidence * 100).toFixed(1)}% độ tin cậy)`;
    
    // Add indicator near the comment
    commentElement.style.position = 'relative';
    commentElement.parentNode.insertBefore(indicator, commentElement.nextSibling);
    
    // Optional: add a subtle border to the original comment
    commentElement.style.borderLeft = `3px solid ${style.color}`;
    commentElement.style.paddingLeft = '10px';
    
    // Blur toxic content (hate speech) if enabled
    if (category === 'hate' && displayOptions.showHate) {
      commentElement.classList.add('toxic-blur');
      
      // Add a button to reveal
      const revealBtn = document.createElement('button');
      revealBtn.className = 'toxic-reveal-btn';
      revealBtn.textContent = 'Hiện nội dung';
      revealBtn.onclick = function() {
        commentElement.classList.remove('toxic-blur');
        revealBtn.remove();
      };
      
      commentElement.parentNode.insertBefore(revealBtn, commentElement.nextSibling);
    }
  });
}
/**
 * Generate a simple hash string
 * @param {string} str - Input string
 * @returns {string} - Hash string
 */
function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
}
/**
 * Vietnamese toxicity labels for UI display
 */
const VIETNAMESE_LABELS = {
  0: "Bình thường",
  1: "Xúc phạm",
  2: "Thù ghét",
  3: "Spam"
};

/**
 * Vietnamese color names for UI display
 */
const VIETNAMESE_COLORS = {
  1: "cam",      // orange for offensive
  2: "đỏ",       // red for hate speech
  3: "tím"       // purple for spam
};

/**
 * Vietnamese interface texts
 */
const VI_TEXTS = {
  revealBtn: "Hiện nội dung",
  revealTooltip: "Nhấn để hiện nội dung bị ẩn",
  tooltipPrefix: "Nội dung này đã được phát hiện là: "
};

/**
 * Get comment selectors for common Vietnamese social platforms
 * Adding more selector patterns for Vietnamese social media platforms
 * @returns {string} - CSS selector
 */
function getVietnameseCommentSelectors() {
  const standard = getCommentSelectors(); // Get standard selectors
  
  // Add more Vietnamese-specific selectors
  // For example, Vietnamese forums, news sites, etc.
  const vietnameseSelectors = [
    // Vietnamese forums
    '.bilutv-comment .content',
    '.phimmoi-comment .text',
    '.forum-comment-content',
    // Vietnamese news sites
    '.vnexpress-comment-body',
    '.vietnamnet-comment-content',
    '.dantri-comment-text',
    // Vietnamese social media with different selectors
    '.zalo-comment-text',
    '.tinhte-comment-body'
  ].join(', ');
  
  return standard + (standard ? ', ' : '') + vietnameseSelectors;
}

/**
 * Apply toxicity indicator with Vietnamese labels
 * @param {Element} commentElement - The comment DOM element
 * @param {Object} prediction - The prediction result
 */
function applyVietnameseToxicityIndicator(commentElement, prediction) {
  if (!highlightToxic || prediction.prediction === 0) {
    return;
  }
  
  // Create toxicity indicator with Vietnamese label
  const indicator = document.createElement('div');
  indicator.className = 'toxic-indicator';
  
  // Set color and Vietnamese label based on toxicity type
  let color, label;
  switch (prediction.prediction) {
    case 1: // Offensive
      color = 'orange';
      label = 'Xúc phạm';
      break;
    case 2: // Hate
      color = 'red';
      label = 'Thù ghét';
      break;
    case 3: // Spam
      color = 'purple';
      label = 'Spam';
      break;
    default:
      return;
  }
  
  indicator.style.backgroundColor = color;
  indicator.textContent = label;
  
  // Add tooltip in Vietnamese
  indicator.title = VI_TEXTS.tooltipPrefix + label.toLowerCase();
  
  // Add indicator near the comment
  commentElement.style.position = 'relative';
  commentElement.parentNode.insertBefore(indicator, commentElement.nextSibling);
  
  // Optional: blur toxic content
  if (prediction.prediction === 2) { // Only blur hate speech
    commentElement.classList.add('toxic-blur');
    
    // Add a button to reveal with Vietnamese text
    const revealBtn = document.createElement('button');
    revealBtn.className = 'toxic-reveal-btn';
    revealBtn.textContent = VI_TEXTS.revealBtn;
    revealBtn.title = VI_TEXTS.revealTooltip;
    revealBtn.onclick = function() {
      commentElement.classList.remove('toxic-blur');
      revealBtn.remove();
    };
    
    commentElement.parentNode.insertBefore(revealBtn, commentElement.nextSibling);
  }
}

// Modifications to popup.js for Vietnamese language support

/**
 * Add Vietnamese language interface to popup
 */
function initializeVietnameseUI() {
  // Map of UI elements to translate
  const translations = {
    '.toggle-label': 'Kích hoạt tiện ích',
    'h2:first-of-type': 'Cài đặt',
    'label[for="threshold"]': 'Ngưỡng nhạy cảm:',
    '#highlight-toxic + span + .checkmark + span': 'Đánh dấu nội dung độc hại',
    'h3': 'Kích hoạt trên nền tảng:',
    '#platform-facebook + span + .checkmark + span': 'Facebook',
    '#platform-youtube + span + .checkmark + span': 'YouTube',
    '#platform-twitter + span + .checkmark + span': 'Twitter',
    'h2:last-of-type': 'Thống kê',
    '#stat-scanned + .stat-label': 'Đã quét',
    '#stat-toxic + .stat-label': 'Độc hại',
    '#stat-clean + .stat-label': 'Bình thường',
    '#reset-stats': 'Đặt lại thống kê',
    '.footer p:first-child': 'Công cụ Phát hiện Ngôn từ Độc hại v1.0.0',
    '.footer p.small': 'Phát triển cho Nghiên cứu'
  };
  
  // Apply translations based on user language preference
  if (navigator.language.startsWith('vi')) {
    Object.entries(translations).forEach(([selector, text]) => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(el => {
        el.textContent = text;
      });
    });
  }
}

// Add to initialize() in popup.js
// document.addEventListener('DOMContentLoaded', () => {
//   loadSettings();
//   initializeVietnameseUI();
// });