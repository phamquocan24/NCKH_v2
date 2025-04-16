/**
 * Popup script for the Toxic Language Detector Extension
 * Handles user settings and statistics for all 4 classification categories
 */

// DOM elements
const enableToggle = document.getElementById('enable-toggle');
const thresholdSlider = document.getElementById('threshold');
const thresholdValue = document.getElementById('threshold-value');
const highlightToxic = document.getElementById('highlight-toxic');
const platformFacebook = document.getElementById('platform-facebook');
const platformYoutube = document.getElementById('platform-youtube');
const platformTwitter = document.getElementById('platform-twitter');

// Statistics elements
const statScanned = document.getElementById('stat-scanned');
const statClean = document.getElementById('stat-clean');
const statOffensive = document.getElementById('stat-offensive');
const statHate = document.getElementById('stat-hate');
const statSpam = document.getElementById('stat-spam');
const resetStatsBtn = document.getElementById('reset-stats');

// Classification visibility toggles
const showClean = document.getElementById('show-clean');
const showOffensive = document.getElementById('show-offensive');
const showHate = document.getElementById('show-hate');
const showSpam = document.getElementById('show-spam');

/**
 * Load all settings and statistics from storage
 */
function loadSettings() {
  chrome.storage.sync.get(null, (data) => {
    // Extension enabled state
    if (enableToggle) {
      enableToggle.checked = data.enabled !== undefined ? data.enabled : true;
    }
    
    // Threshold
    if (thresholdSlider && thresholdValue && data.threshold) {
      thresholdSlider.value = data.threshold;
      thresholdValue.textContent = data.threshold;
    }
    
    // Highlight toxic content
    if (highlightToxic) {
      highlightToxic.checked = data.highlightToxic !== undefined ? data.highlightToxic : true;
    }
    
    // Platform settings
    if (data.platforms) {
      if (platformFacebook) {
        platformFacebook.checked = data.platforms.facebook !== undefined ? data.platforms.facebook : true;
      }
      if (platformYoutube) {
        platformYoutube.checked = data.platforms.youtube !== undefined ? data.platforms.youtube : true;
      }
      if (platformTwitter) {
        platformTwitter.checked = data.platforms.twitter !== undefined ? data.platforms.twitter : true;
      }
    }
    
    // Display options settings
    if (data.displayOptions) {
      if (showClean) {
        showClean.checked = data.displayOptions.showClean !== undefined ? data.displayOptions.showClean : true;
      }
      if (showOffensive) {
        showOffensive.checked = data.displayOptions.showOffensive !== undefined ? data.displayOptions.showOffensive : true;
      }
      if (showHate) {
        showHate.checked = data.displayOptions.showHate !== undefined ? data.displayOptions.showHate : true;
      }
      if (showSpam) {
        showSpam.checked = data.displayOptions.showSpam !== undefined ? data.displayOptions.showSpam : true;
      }
    }
    
    // Statistics
    loadStatistics(data.stats);
  });
}

/**
 * Load statistics from storage data
 * @param {Object} stats - Statistics data from storage
 */
function loadStatistics(stats) {
  const defaultStats = {
    scanned: 0,
    clean: 0,
    offensive: 0,
    hate: 0,
    spam: 0
  };
  
  // Use provided stats or defaults
  const currentStats = stats || defaultStats;
  
  // Update UI
  if (statScanned) statScanned.textContent = currentStats.scanned || 0;
  if (statClean) statClean.textContent = currentStats.clean || 0;
  if (statOffensive) statOffensive.textContent = currentStats.offensive || 0;
  if (statHate) statHate.textContent = currentStats.hate || 0;
  if (statSpam) statSpam.textContent = currentStats.spam || 0;
}

/**
 * Save all settings to storage
 */
function saveSettings() {
  const settings = {
    enabled: enableToggle ? enableToggle.checked : true,
    threshold: thresholdSlider ? parseFloat(thresholdSlider.value) : 0.7,
    highlightToxic: highlightToxic ? highlightToxic.checked : true,
    platforms: {
      facebook: platformFacebook ? platformFacebook.checked : true,
      youtube: platformYoutube ? platformYoutube.checked : true,
      twitter: platformTwitter ? platformTwitter.checked : true
    },
    displayOptions: {
      showClean: showClean ? showClean.checked : true,
      showOffensive: showOffensive ? showOffensive.checked : true,
      showHate: showHate ? showHate.checked : true,
      showSpam: showSpam ? showSpam.checked : true
    }
  };
  
  chrome.storage.sync.set(settings, () => {
    // Notify content scripts that settings have changed
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, {
          action: "settingsUpdated",
          settings: settings
        }).catch(err => console.log("Could not send settings update to content script", err));
      }
    });
  });
}

/**
 * Update threshold value display
 */
function updateThresholdValue() {
  if (thresholdSlider && thresholdValue) {
    thresholdValue.textContent = thresholdSlider.value;
  }
}

/**
 * Reset all statistics
 */
function resetStats() {
  // Default statistics
  const defaultStats = {
    scanned: 0,
    clean: 0,
    offensive: 0,
    hate: 0,
    spam: 0
  };
  
  // Send reset message to background script
  chrome.runtime.sendMessage({ action: "resetStats" }, (response) => {
    if (response && response.success) {
      // Update UI with reset stats
      loadStatistics(defaultStats);
    }
  });
}

/**
 * Toggle advanced settings visibility
 */
function toggleAdvancedSettings() {
  const advancedSettings = document.getElementById('advanced-settings');
  if (advancedSettings) {
    const isHidden = advancedSettings.style.display === 'none';
    advancedSettings.style.display = isHidden ? 'block' : 'none';
    
    // Update toggle button text
    const toggleBtn = document.getElementById('toggle-advanced');
    if (toggleBtn) {
      toggleBtn.textContent = isHidden ? 'Ẩn cài đặt nâng cao' : 'Hiện cài đặt nâng cao';
    }
  }
}

/**
 * Initialize the popup UI
 */
function initializePopup() {
  // Load settings and stats
  loadSettings();
  
  // Set up event listeners
  if (enableToggle) enableToggle.addEventListener('change', saveSettings);
  
  if (thresholdSlider) {
    thresholdSlider.addEventListener('input', updateThresholdValue);
    thresholdSlider.addEventListener('change', saveSettings);
  }
  
  if (highlightToxic) highlightToxic.addEventListener('change', saveSettings);
  
  // Platform toggles
  if (platformFacebook) platformFacebook.addEventListener('change', saveSettings);
  if (platformYoutube) platformYoutube.addEventListener('change', saveSettings);
  if (platformTwitter) platformTwitter.addEventListener('change', saveSettings);
  
  // Display option toggles
  if (showClean) showClean.addEventListener('change', saveSettings);
  if (showOffensive) showOffensive.addEventListener('change', saveSettings);
  if (showHate) showHate.addEventListener('change', saveSettings);
  if (showSpam) showSpam.addEventListener('change', saveSettings);
  
  // Reset statistics button
  if (resetStatsBtn) resetStatsBtn.addEventListener('click', resetStats);
  
  // Advanced settings toggle
  const toggleBtn = document.getElementById('toggle-advanced');
  if (toggleBtn) toggleBtn.addEventListener('click', toggleAdvancedSettings);
  
  // Version display
  const versionElement = document.getElementById('version');
  if (versionElement) {
    chrome.runtime.getManifest().version;
    versionElement.textContent = `v${chrome.runtime.getManifest().version}`;
  }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePopup);

// Handle real-time updates from other parts of the extension
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'sync') {
    // If stats changed, update the display
    if (changes.stats) {
      loadStatistics(changes.stats.newValue);
    }
  }
});