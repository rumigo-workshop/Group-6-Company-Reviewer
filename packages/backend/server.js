const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

// Sample LeetCode problems
const problems = [{
        id: 1,
        title: "Two Sum",
        difficulty: "Easy",
        language: "C++"
    },
    {
        id: 2,
        title: "Valid Parentheses",
        difficulty: "Easy",
        language: "C++"
    },
    {
        id: 3,
        title: "Longest Substring Without Repeating Characters",
        difficulty: "Medium",
        language: "C++"
    }
];

// Basic API route
app.get("/", (req, res) => {
    res.send("LeetCode API is running!");
});

// GET all problems
app.get("/api/problems", (req, res) => {
    res.json(problems);
});

// GET a specific problem by ID
app.get("/api/problems/:id", (req, res) => {
    const id = Number(req.params.id);

    const problem = problems.find(p => p.id === id);

    if (!problem) {
        return res.status(404).json({
            message: "Problem not found"
        });
    }

    res.json(problem);
});

// Start server
app.listen(5000, () => {
    console.log("Backend running at http://localhost:5000");
});