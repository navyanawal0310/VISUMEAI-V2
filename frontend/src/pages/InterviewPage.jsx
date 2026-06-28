import { useLocation, Navigate, useNavigate } from "react-router-dom";
import { useState, useEffect, useRef, useCallback } from "react";

// ─── useSpeech ───────────────────────────────────────────────────────────────

function useSpeech() {
  const cancel = useCallback(() => {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  }, []);

  const speak = useCallback((text) => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.rate = 0.95;
    utt.pitch = 1;
    window.speechSynthesis.speak(utt);
  }, []);

  return { speak, cancel };
}

// ─── ProgressBar ─────────────────────────────────────────────────────────────

function ProgressBar({ current, total }) {
  const pct = Math.round(((current + 1) / total) * 100);
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs font-medium text-gray-400 mb-1.5">
        <span>Progress</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            width: `${pct}%`,
            background: "linear-gradient(90deg, #7c3aed 0%, #a855f7 100%)",
          }}
        />
      </div>
    </div>
  );
}

// ─── RecordingControls ────────────────────────────────────────────────────────

function RecordingControls({ isRecording, onStart, onStop, timer }) {
  const mins = String(Math.floor(timer / 60)).padStart(2, "0");
  const secs = String(timer % 60).padStart(2, "0");

  return (
    <div className="flex items-center gap-3">
      <div
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-mono font-semibold transition-colors ${
          isRecording
            ? "bg-red-50 text-red-600 ring-1 ring-red-200"
            : "bg-gray-100 text-gray-400"
        }`}
      >
        {isRecording && (
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        )}
        {mins}:{secs}
      </div>

      {!isRecording ? (
        <button
          onClick={onStart}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white shadow-sm transition-all active:scale-95"
          style={{ background: "linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)" }}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 1a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V4a3 3 0 0 1 3-3z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 10a7 7 0 0 1-14 0M12 17v4M8 21h8" />
          </svg>
          Start Recording
        </button>
      ) : (
        <button
          onClick={onStop}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold text-white bg-red-500 hover:bg-red-600 shadow-sm transition-all active:scale-95"
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
            <rect x="5" y="5" width="14" height="14" rx="2" />
          </svg>
          Stop Recording
        </button>
      )}
    </div>
  );
}

// ─── WebcamPanel ──────────────────────────────────────────────────────────────

function WebcamPanel({ videoRef, isRecording, camError }) {
  return (
    <div className="relative w-full aspect-video bg-gray-900 rounded-2xl overflow-hidden shadow-inner">
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover"
      />

      {camError ? (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-gray-500 bg-gray-900">
          <svg className="w-10 h-10 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M18.364 18.364A9 9 0 0 0 5.636 5.636m12.728 12.728A9 9 0 0 1 5.636 5.636m12.728 12.728L5.636 5.636" />
          </svg>
          <p className="text-xs text-gray-500 px-4 text-center">{camError}</p>
        </div>
      ) : null}

      {isRecording && (
        <div className="absolute top-3 left-3 flex items-center gap-1.5 bg-red-600 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow z-10">
          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
          LIVE
        </div>
      )}

      {[
        "top-2 left-2 border-t-2 border-l-2 rounded-tl",
        "top-2 right-2 border-t-2 border-r-2 rounded-tr",
        "bottom-2 left-2 border-b-2 border-l-2 rounded-bl",
        "bottom-2 right-2 border-b-2 border-r-2 rounded-br",
      ].map((cls, i) => (
        <div key={i} className={`absolute w-5 h-5 border-violet-500 opacity-50 z-10 ${cls}`} />
      ))}
    </div>
  );
}

// ─── QuestionCard ─────────────────────────────────────────────────────────────

function QuestionCard({
  question, index, total,
  onPrev, onNext, onListenAgain,
  nextDisabled, isLastQuestion,
  allAnswered, onFinish, isSubmitting,
}) {
  // On the last question: show Finish Interview instead of Next
  const showFinish = isLastQuestion;
  const finishReady = allAnswered && !isSubmitting;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 flex flex-col gap-6">
      {/* Eyebrow */}
      <div className="flex items-center gap-2">
        <span
          className="text-xs font-bold tracking-widest uppercase px-3 py-1 rounded-full text-violet-700"
          style={{ background: "rgba(124,58,237,0.08)" }}
        >
          Question {index + 1} of {total}
        </span>
      </div>

      {/* Question text */}
      <p className="text-2xl font-semibold text-gray-900 leading-snug min-h-[4rem]">
        {question.question}
      </p>

      {/* Listen Again */}
      <button
        onClick={onListenAgain}
        className="self-start flex items-center gap-2 text-sm font-medium text-violet-600 hover:text-violet-800 transition-colors group"
      >
        <span className="w-8 h-8 rounded-full flex items-center justify-center border border-violet-200 group-hover:border-violet-400 transition-colors">
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 0 1 0 7.072M12 6a7 7 0 0 1 0 12M9 9a3 3 0 0 0 0 6" />
          </svg>
        </span>
        Listen Again
      </button>

      {/* Navigation */}
      <div className="flex justify-between pt-2 border-t border-gray-100">
        <button
          disabled={index === 0}
          onClick={onPrev}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-gray-600 bg-gray-100 hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>

        <div className="flex flex-col items-end gap-1">
          {showFinish ? (
            /* ── Finish Interview button ── */
            <button
              disabled={!finishReady}
              onClick={onFinish}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white shadow-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-95"
              style={{
                background: finishReady
                  ? "linear-gradient(135deg, #059669 0%, #10b981 100%)"
                  : "#9ca3af",
              }}
            >
              {isSubmitting ? (
                <>
                  {/* Spinner */}
                  <svg
                    className="w-4 h-4 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12" cy="12" r="10"
                      stroke="currentColor" strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                    />
                  </svg>
                  Uploading…
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  Finish Interview
                </>
              )}
            </button>
          ) : (
            /* ── Next button ── */
            <button
              disabled={nextDisabled}
              onClick={onNext}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white shadow-sm disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95"
              style={{
                background: nextDisabled
                  ? "#9ca3af"
                  : "linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)",
              }}
            >
              Next
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}

          {/* Helper hints */}
          {!showFinish && nextDisabled && (
            <p className="text-xs text-gray-400">Record your answer to continue</p>
          )}
          {showFinish && !allAnswered && (
            <p className="text-xs text-gray-400">Record your answer to finish</p>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── ProcessingScreen ─────────────────────────────────────────────────────────

export function ProcessingScreen() {
  return (
    <div className="min-h-screen bg-gray-50 font-sans flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #7c3aed, #a855f7)" }}
          >
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <span className="text-lg font-bold text-gray-900 tracking-tight">VisumeAI</span>
        </div>
      </header>

      {/* Body */}
      <div className="flex-1 flex items-center justify-center px-6">
        <div className="text-center max-w-sm">
          {/* Animated ring */}
          <div className="relative w-20 h-20 mx-auto mb-8">
            <div
              className="absolute inset-0 rounded-full animate-spin"
              style={{
                background: "conic-gradient(from 0deg, #7c3aed, #a855f7, transparent)",
              }}
            />
            <div className="absolute inset-1 bg-gray-50 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-violet-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            Processing Interview…
          </h1>
          <p className="text-sm text-gray-500 leading-relaxed">
            Your responses have been uploaded. We're analysing your answers — this usually takes a minute or two.
          </p>

          {/* Pulsing step list */}
          <div className="mt-8 space-y-3 text-left">
            {[
              { label: "Transcribing audio responses", done: true },
              { label: "Evaluating technical accuracy", done: false },
              { label: "Generating feedback report", done: false },
            ].map(({ label, done }, i) => (
              <div key={i} className="flex items-center gap-3">
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                    done
                      ? "bg-violet-100 text-violet-600"
                      : "bg-gray-100"
                  }`}
                >
                  {done ? (
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-gray-300 animate-pulse" />
                  )}
                </span>
                <span className={`text-sm ${done ? "text-gray-700 font-medium" : "text-gray-400"}`}>
                  {label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── InterviewPage ────────────────────────────────────────────────────────────

export default function InterviewPage() {
  const location = useLocation();
  const navigate = useNavigate();

  if (!location.state?.questions) {
    return <Navigate to="/candidate" replace />;
  }

  const { questions, difficulty, resumeAnalysis, jobDescription } = location.state;

  // ── Core state ──
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [timer, setTimer] = useState(0);
  const [recordings, setRecordings] = useState(() => Array(questions.length).fill(null));
  const [camError, setCamError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // ── Refs ──
  const videoRef = useRef(null);
  const camStreamRef = useRef(null);
  const micStreamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerIntervalRef = useRef(null);

  const { speak, cancel } = useSpeech();

  // ── Webcam on mount ──────────────────────────────────────────────────────
  useEffect(() => {
    let active = true;
    navigator.mediaDevices
      .getUserMedia({ video: true, audio: false })
      .then((stream) => {
        if (!active) { stream.getTracks().forEach(t => t.stop()); return; }
        camStreamRef.current = stream;
        if (videoRef.current) videoRef.current.srcObject = stream;
      })
      .catch((err) => {
        if (!active) return;
        setCamError("Camera access denied. Check your browser permissions.");
        console.warn("Webcam error:", err);
      });

    return () => {
      active = false;
      camStreamRef.current?.getTracks().forEach(t => t.stop());
    };
  }, []);

  // ── Speak on question change ─────────────────────────────────────────────
  useEffect(() => {
    const text = questions[currentQuestion]?.question;
    if (text) speak(text);
    return () => cancel();
  }, [currentQuestion]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Global cleanup on unmount ────────────────────────────────────────────
  useEffect(() => {
    return () => {
      cancel();
      clearInterval(timerIntervalRef.current);
      micStreamRef.current?.getTracks().forEach(t => t.stop());
      camStreamRef.current?.getTracks().forEach(t => t.stop());
      if (mediaRecorderRef.current?.state !== "inactive") {
        mediaRecorderRef.current?.stop();
      }
    };
  }, [cancel]);

  // ── Timer ────────────────────────────────────────────────────────────────
  const startTimer = () => {
    setTimer(0);
    clearInterval(timerIntervalRef.current);
    timerIntervalRef.current = setInterval(() => setTimer(t => t + 1), 1000);
  };

  const stopTimer = () => clearInterval(timerIntervalRef.current);

  // ── Recording ────────────────────────────────────────────────────────────
  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      micStreamRef.current = stream;
      chunksRef.current = [];

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setRecordings(prev => {
          const next = [...prev];
          next[currentQuestion] = blob;
          return next;
        });
        micStreamRef.current?.getTracks().forEach(t => t.stop());
        micStreamRef.current = null;
      };

      recorder.start();
      startTimer();
      setIsRecording(true);
    } catch (err) {
      console.warn("Microphone error:", err);
      alert("Microphone access denied. Please allow microphone permissions and try again.");
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current?.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    stopTimer();
    setIsRecording(false);
  };

  // ── Navigation ───────────────────────────────────────────────────────────
  const goNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(q => q + 1);
      setTimer(0);
    }
  };

  const goPrev = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(q => q - 1);
      setTimer(0);
    }
  };

  // ── Submit ───────────────────────────────────────────────────────────────
  const handleFinish = async () => {
    setSubmitError(null);
    setIsSubmitting(true);

    try {
      const form = new FormData();

      // Append each recording as a separate file field
      recordings.forEach((blob, i) => {
        if (blob) {
          form.append(`recording_${i}`, blob, `question_${i + 1}.webm`);
        }
      });

      // Append interview metadata as JSON
      form.append("metadata", JSON.stringify({
        difficulty,
        question_count: questions.length,
        questions: questions.map((q, i) => ({
          index: i,
          question: q.question,
          category: q.category ?? null,
        })),
        resume_analysis: resumeAnalysis ?? null,
        job_description: jobDescription ?? null,
      }));

      const res = await fetch("/submit-interview", {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const detail = await res.text();
        throw new Error(`Upload failed (${res.status}): ${detail}`);
      }

      // Stop webcam before navigating away
      camStreamRef.current?.getTracks().forEach(t => t.stop());

      navigate("/processing", { replace: true });
    } catch (err) {
      console.error("Submission error:", err);
      setSubmitError(err.message ?? "Upload failed. Please try again.");
      setIsSubmitting(false);
    }
  };

  // ── Derived state ────────────────────────────────────────────────────────
  const isLastQuestion = currentQuestion === questions.length - 1;
  const hasRecording   = !!recordings[currentQuestion];
  const allAnswered    = recordings.every(Boolean);
  // Next is disabled when there's no recording for the current question
  const nextDisabled   = !hasRecording;

  const difficultyColors = {
    Easy:   { bg: "bg-emerald-50", text: "text-emerald-700", ring: "ring-emerald-200" },
    Medium: { bg: "bg-amber-50",   text: "text-amber-700",   ring: "ring-amber-200"   },
    Hard:   { bg: "bg-red-50",     text: "text-red-700",     ring: "ring-red-200"     },
  };
  const dc = difficultyColors[difficulty] ?? difficultyColors.Medium;

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50 font-sans">

      {/* ── Header ── */}
      <header className="bg-white border-b border-gray-100 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center"
              style={{ background: "linear-gradient(135deg, #7c3aed, #a855f7)" }}
            >
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <span className="text-lg font-bold text-gray-900 tracking-tight">VisumeAI</span>
          </div>

          <div className="flex items-center gap-3">
            <span className={`text-xs font-semibold px-3 py-1 rounded-full ring-1 ${dc.bg} ${dc.text} ${dc.ring}`}>
              {difficulty}
            </span>
            <span className="text-sm text-gray-400 hidden sm:block">AI Mock Interview</span>
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="max-w-6xl mx-auto px-6 py-8">

        <div className="mb-8">
          <ProgressBar current={currentQuestion} total={questions.length} />
        </div>

        {/* Submit error banner */}
        {submitError && (
          <div className="mb-6 flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
            <svg className="w-4 h-4 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            </svg>
            <span>{submitError}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-start">

          {/* Left — question + nav */}
          <div className="lg:col-span-3">
            <QuestionCard
              question={questions[currentQuestion]}
              index={currentQuestion}
              total={questions.length}
              onPrev={goPrev}
              onNext={goNext}
              onListenAgain={() => speak(questions[currentQuestion]?.question)}
              nextDisabled={nextDisabled}
              isLastQuestion={isLastQuestion}
              allAnswered={allAnswered}
              onFinish={handleFinish}
              isSubmitting={isSubmitting}
            />
          </div>

          {/* Right — webcam + recording */}
          <div className="lg:col-span-2 flex flex-col gap-4">

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
                Your Camera
              </p>
              <WebcamPanel
                videoRef={videoRef}
                isRecording={isRecording}
                camError={camError}
              />
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
                Response Recording
              </p>
              <RecordingControls
                isRecording={isRecording}
                timer={timer}
                onStart={handleStartRecording}
                onStop={handleStopRecording}
              />

              <p className="mt-3 text-xs text-gray-400">
                {isRecording
                  ? "Recording in progress — speak clearly into your microphone."
                  : hasRecording
                  ? "Answer recorded. You can re-record or continue."
                  : "Press Start Recording when you're ready to answer."}
              </p>

              {hasRecording && !isRecording && (
                <div className="mt-3 flex items-center gap-2 text-xs font-medium text-emerald-700 bg-emerald-50 px-3 py-2 rounded-lg">
                  <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  Answer saved for question {currentQuestion + 1}
                </div>
              )}
            </div>

            {questions.length > 1 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
                  Answers
                </p>
                <div className="flex flex-wrap gap-2">
                  {questions.map((_, i) => (
                    <button
                      key={i}
                      onClick={() => { if (!isRecording && !isSubmitting) setCurrentQuestion(i); }}
                      className={`w-8 h-8 rounded-full text-xs font-bold transition-all ${
                        i === currentQuestion ? "ring-2 ring-violet-500 ring-offset-1" : ""
                      } ${
                        recordings[i] ? "bg-violet-600 text-white" : "bg-gray-100 text-gray-400"
                      }`}
                      title={recordings[i] ? `Question ${i + 1} — recorded` : `Question ${i + 1} — not yet recorded`}
                    >
                      {i + 1}
                    </button>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}