import * as socket from "./sockets.js";
import * as navbar from "./navbar.js";
import * as tabnav from "./tabnav.js";
import * as modal from "./modal.js";
import * as mapcanvas from "./mapcanvas.js";
import * as upload from "./upload.js";
import * as upload_progress from "./upload_progress.js";
import * as blender from "./blender.js";

try {
  document.addEventListener('DOMContentLoaded', () => {
    // init sockets
    const socketInstance = socket.init();
  
    // init navbar
    const navTogglerBtn = document.getElementById('navTogglerBtn');
    navbar.init(navTogglerBtn);
  
    //init tabnav
    tabnav.init();
    
    // init mapcanvas
    const openCanvasBtn = document.getElementById('openCanvasBtn');
    const mapCanvas = document.getElementById('mapCanvas');
    const closeCanvasBtn = document.getElementById('closeCanvasBtn');
    mapcanvas.init(openCanvasBtn, mapCanvas, closeCanvasBtn);
    
    // init upload
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const fileInputBtn = document.getElementById('fileInputBtn');
    const fileList = document.getElementById('fileList');
    const uploadModalBtn = document.getElementById('uploadModalBtn');
    const uploadForm = document.getElementById('uploadForm');
    upload.init(fileInput, fileName, fileInputBtn, fileList, uploadModalBtn, uploadForm);
  
    // init modal
    const uploadNavBtn = document.getElementById('uploadNavBtn');
    const closeModal = document.getElementById('closeModal');
    const uploadModal = document.getElementById('uploadModal');
    const overallProgressDiv = document.querySelector('.total-progress');
    modal.init(uploadNavBtn, closeModal, uploadModal, fileInput, overallProgressDiv);
  
    // init upload progress handler
    const state = document.getElementById('state');
    const status = document.getElementById('status');
    const consoleOutput = document.getElementById('consoleOutput');
    const totalProgressDail = document.getElementById('totalProgressDail');
    const uploadProgressBar = document.getElementById('uploadProgress');
    const progressText = document.getElementById('progressText');
    upload_progress.init(socketInstance, state, status, consoleOutput, totalProgressDail, uploadProgressBar, progressText);
  
    // init blender
    blender.init();
    
  });
} catch (error) {
  console.error(error);
}

