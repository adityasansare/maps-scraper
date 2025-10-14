import React, { useState } from "react";
import {
  Container,
  TextField,
  Button,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  Link,
  Box,
} from "@mui/material";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleScrape = async () => {
    if (!query.trim()) {
      setError("Please enter a search query.");
      return;
    }
    setError("");
    setLoading(true);
    setResults([]);

    try {
      const res = await fetch("http://localhost:8000/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Scraping failed");
      }

      const data = await res.json();
      if (data.success) {
        setResults(data.data);
      } else {
        setError("Failed to fetch data.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = async () => {
    try {
      const res = await fetch("http://localhost:8000/download_csv");
      if (!res.ok) throw new Error("Failed to download CSV");

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "mumbai_places.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Download failed: " + err.message);
    }
  };

  return (
    <Container maxWidth="md" sx={{ my: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Google Maps Scraper
      </Typography>

      <TextField
        fullWidth
        label="Enter Search Query"
        variant="outlined"
        value={query}
        disabled={loading}
        onChange={(e) => setQuery(e.target.value)}
        placeholder='e.g., "Doctors in Dadar East"'
        margin="normal"
      />

      <Box sx={{ position: "relative", display: "inline-flex", alignItems: "center" }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleScrape}
          disabled={loading}
          size="large"
          sx={{ mr: 2 }}
        >
          {loading ? "Scraping..." : "Start Scrape"}
        </Button>
        {loading && (
          <CircularProgress
            size={24}
            sx={{ position: "absolute", right: -36, color: "primary.main" }}
          />
        )}
      </Box>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {results.length > 0 && !loading && (
        <>
          <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>
            Scraped Results ({results.length})
          </Typography>

          <TableContainer component={Paper}>
            <Table aria-label="scraped data table" size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Rating</TableCell>
                  <TableCell>Reviews</TableCell>
                  <TableCell>Address</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Website</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {results.map((row, idx) => (
                  <TableRow key={idx}>
                    <TableCell>{row.name || "-"}</TableCell>
                    <TableCell>{row.category || "-"}</TableCell>
                    <TableCell>{row.rating || "-"}</TableCell>
                    <TableCell>{row.reviews || "-"}</TableCell>
                    <TableCell>{row.address || "-"}</TableCell>
                    <TableCell>{row.phone || "-"}</TableCell>
                    <TableCell>
                      {row.website ? (
                        <Link href={row.website} target="_blank" rel="noopener">
                          Website
                        </Link>
                      ) : (
                        "-"
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Button
            variant="outlined"
            sx={{ mt: 3 }}
            onClick={downloadCSV}
            disabled={loading || results.length === 0}
            size="large"
          >
            Download CSV
          </Button>
        </>
      )}
    </Container>
  );
}

export default App;
