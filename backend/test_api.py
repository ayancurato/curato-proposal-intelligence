import httpx
import asyncio

async def run():
    url_upload = "http://localhost:8000/api/upload"
    pdf_path = r"C:\Users\ayaan\OneDrive\Desktop\Curato Proposal Intelligence Agent\uploads\116ac0afe8724f2095d04017249a9fc4.pdf"
    
    files = {
        'files': ('test.pdf', open(pdf_path, 'rb'), 'application/pdf')
    }
    async with httpx.AsyncClient(timeout=300.0) as client:
        print("Sending upload request...")
        response = await client.post(url_upload, files=files)
        print("Upload Status:", response.status_code)
        if response.status_code == 201:
            data = response.json()
            session_id = data.get("id")
            print("Session ID:", session_id)
            
            print("Starting analysis...")
            start_res = await client.post(f"http://localhost:8000/api/analysis/{session_id}/start")
            print("Start status:", start_res.status_code)
            
            # Now poll status
            for _ in range(60):
                await asyncio.sleep(5)
                res = await client.get(f"http://localhost:8000/api/analysis/{session_id}/status")
                if res.status_code == 200:
                    d = res.json()
                    status = d.get("status")
                    print("Status:", status)
                    if status in ["completed", "failed"]:
                        print("Finished with status:", status)
                        if status == "completed":
                            dashboard_res = await client.get(f"http://localhost:8000/api/analysis/{session_id}")
                            if dashboard_res.status_code == 200:
                                dash = dashboard_res.json()
                                print("Quick Stats:", dash.get("quick_stats"))
                                print("Analysis dimensions:", len(dash.get("comparison", {}).get("dimensions", [])))
                        break
        else:
            print("Error:", response.text)

if __name__ == "__main__":
    asyncio.run(run())
