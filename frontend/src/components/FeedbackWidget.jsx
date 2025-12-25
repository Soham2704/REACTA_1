import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { sendFeedback } from '../api';
import { motion } from 'framer-motion';

const FeedbackWidget = ({ reportData }) => {
    const [status, setStatus] = useState('idle'); // idle, sending, sentinel

    if (!reportData) return null;

    const handleVote = async (type) => {
        setStatus('sending');
        try {
            await sendFeedback({
                project_id: reportData.project_id,
                case_id: reportData.case_id,
                user_feedback: type,
                input_case: { parameters: reportData.inputs },
                output_report: reportData
            });
            setStatus('sent');
            setTimeout(() => setStatus('idle'), 3000);
        } catch (err) {
            console.error(err);
            setStatus('error');
        }
    };

    if (status === 'sent') {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="fixed bottom-8 right-8 z-50 glass-panel p-4 rounded-xl flex items-center gap-3 text-dark-success border-dark-success/20 shadow-2xl"
            >
                <ThumbsUp size={20} fill="currentColor" />
                <span className="font-medium">Feedback Recorded. Training RL Model...</span>
            </motion.div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="fixed bottom-8 right-8 z-50 glass-panel p-2 rounded-xl flex items-center gap-2 shadow-2xl"
        >
            <span className="text-xs font-bold uppercase text-gray-500 px-2">Was this helpful?</span>
            <button
                onClick={() => handleVote('up')}
                className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-dark-success transition-colors"
            >
                <ThumbsUp size={20} />
            </button>
            <div className="w-px h-4 bg-white/10"></div>
            <button
                onClick={() => handleVote('down')}
                className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-dark-error transition-colors"
            >
                <ThumbsDown size={20} />
            </button>
        </motion.div>
    );
};

export default FeedbackWidget;
